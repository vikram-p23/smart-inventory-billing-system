import os, json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import date, timedelta
from config import supabase

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

class ChatMsg(BaseModel):
    message: str
    session_id: Optional[str] = None

async def fetch_context(query: str) -> dict:
    ctx = {}
    q = query.lower()
    today = str(date.today())

    if any(w in q for w in ["today", "today's"]):
        r = supabase.table("sales").select("total_amount, invoice_number, payment_method, created_at").gte("created_at", f"{today}T00:00:00").lte("created_at", f"{today}T23:59:59").execute()
        ctx["today_revenue"] = round(sum(s["total_amount"] for s in r.data), 2)
        ctx["today_count"] = len(r.data)

    if any(w in q for w in ["week", "weekly", "7 days"]):
        ws = str(date.today() - timedelta(days=7))
        r = supabase.table("sales").select("total_amount").gte("created_at", f"{ws}T00:00:00").execute()
        ctx["weekly_revenue"] = round(sum(s["total_amount"] for s in r.data), 2)
        ctx["weekly_count"] = len(r.data)

    if any(w in q for w in ["month", "monthly"]):
        ms = str(date.today().replace(day=1))
        r = supabase.table("sales").select("total_amount").gte("created_at", f"{ms}T00:00:00").execute()
        ctx["monthly_revenue"] = round(sum(s["total_amount"] for s in r.data), 2)

    if any(w in q for w in ["total revenue", "all time", "overall"]):
        r = supabase.table("sales").select("total_amount").execute()
        ctx["total_revenue"] = round(sum(s["total_amount"] for s in r.data), 2)
        ctx["total_transactions"] = len(r.data)

    if any(w in q for w in ["low stock", "out of stock", "reorder", "shortage"]):
        r = supabase.table("products").select("name, category, stock_quantity, low_stock_threshold").execute()
        ctx["low_stock"] = [p for p in r.data if p["stock_quantity"] <= p["low_stock_threshold"]]

    if any(w in q for w in ["product", "inventory", "stock"]):
        r = supabase.table("products").select("name, category, stock_quantity, selling_price").execute()
        ctx["total_products"] = len(r.data)
        ctx["inventory_value"] = round(sum(p["stock_quantity"] * float(p["selling_price"]) for p in r.data), 2)

    if any(w in q for w in ["top", "best", "popular", "most sold"]):
        items = supabase.table("sale_items").select("product_name, quantity, total_price").execute().data
        totals = {}
        for i in items:
            n = i["product_name"]
            if n not in totals: totals[n] = {"qty": 0, "rev": 0}
            totals[n]["qty"] += i["quantity"]
            totals[n]["rev"] += float(i.get("total_price") or 0)
        ctx["top_products"] = sorted([{"name": k, **v} for k, v in totals.items()], key=lambda x: x["qty"], reverse=True)[:5]

    if any(w in q for w in ["supplier", "vendor", "distributor"]):
        r = supabase.table("suppliers").select("name, contact_person, phone").execute()
        ctx["suppliers"] = r.data
        ctx["total_suppliers"] = len(r.data)

    if any(w in q for w in ["purchase", "procurement", "order"]):
        r = supabase.table("purchases").select("supplier_name, product_name, quantity, total_cost, purchase_date").order("created_at", desc=True).limit(5).execute()
        ctx["recent_purchases"] = r.data

    return ctx

def rule_response(message: str, ctx: dict) -> str:
    lines = []
    if "today_revenue" in ctx:
        lines += [f"📊 **Today's Sales**", f"• Revenue: ₹{ctx['today_revenue']:,.2f}", f"• Transactions: {ctx['today_count']}"]
    if "weekly_revenue" in ctx:
        lines += [f"\n📅 **This Week**", f"• Revenue: ₹{ctx['weekly_revenue']:,.2f}", f"• Transactions: {ctx['weekly_count']}"]
    if "monthly_revenue" in ctx:
        lines += [f"\n🗓️ **This Month**", f"• Revenue: ₹{ctx['monthly_revenue']:,.2f}"]
    if "total_revenue" in ctx:
        lines += [f"\n💰 **All-Time**", f"• Total Revenue: ₹{ctx['total_revenue']:,.2f}", f"• Total Transactions: {ctx['total_transactions']}"]
    if "low_stock" in ctx:
        items = ctx["low_stock"]
        lines.append(f"\n⚠️ **Low Stock — {len(items)} item(s)**")
        for p in items[:8]: lines.append(f"• {p['name']}: {p['stock_quantity']} left (threshold: {p['low_stock_threshold']})")
    if "top_products" in ctx:
        lines.append(f"\n🏆 **Top Selling Products**")
        for i, p in enumerate(ctx["top_products"], 1): lines.append(f"{i}. {p['name']} — {p['qty']} units (₹{p['rev']:,.2f})")
    if "total_products" in ctx:
        lines += [f"\n📦 **Inventory**", f"• Total Products: {ctx['total_products']}", f"• Inventory Value: ₹{ctx['inventory_value']:,.2f}"]
    if "total_suppliers" in ctx:
        lines.append(f"\n🏭 **Suppliers: {ctx['total_suppliers']}**")
        for s in ctx.get("suppliers", [])[:3]: lines.append(f"• {s['name']} — {s.get('contact_person','N/A')} ({s.get('phone','N/A')})")
    if "recent_purchases" in ctx:
        lines.append(f"\n🛒 **Recent Procurements**")
        for p in ctx["recent_purchases"]: lines.append(f"• {p['product_name']} from {p['supplier_name']}: {p['quantity']} units @ ₹{p['total_cost']:,.2f} on {p['purchase_date']}")
    if not lines:
        return ("I can help with:\n• **Today's sales** — 'What are today's sales?'\n• **Revenue** — 'Total revenue this week'\n"
                "• **Low stock** — 'Show low stock items'\n• **Top products** — 'Best selling products'\n"
                "• **Inventory** — 'How many products do we have?'\n• **Suppliers** — 'List our suppliers'")
    return "\n".join(lines)

async def ai_response(message: str, ctx: dict) -> str:
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        ctx_str = json.dumps(ctx, indent=2, default=str) if ctx else "No specific data."
        r = client.messages.create(
            model="claude-sonnet-4-20250514", max_tokens=600,
            system="You are RetailBot, AI assistant for a retail store. Answer queries using the provided store data. Format numbers as Indian Rupees (₹). Be concise and data-driven.",
            messages=[{"role": "user", "content": f"Store data:\n{ctx_str}\n\nQuery: {message}"}]
        )
        return r.content[0].text
    except Exception:
        return rule_response(message, ctx)

@router.post("/")
async def chat(msg: ChatMsg):
    try:
        if not msg.message.strip(): raise HTTPException(400, "Empty message")
        ctx = await fetch_context(msg.message)
        response = await ai_response(msg.message, ctx) if ANTHROPIC_API_KEY else rule_response(msg.message, ctx)
        return {"success": True, "response": response, "has_data": bool(ctx)}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/suggestions")
async def suggestions():
    return {"success": True, "suggestions": [
        "What are today's sales?", "Show low stock items", "Total revenue this week",
        "Best selling products", "List our suppliers", "Monthly revenue", "Recent procurements", "Total inventory value"
    ]}
