from fastapi import APIRouter, HTTPException
from datetime import date, timedelta
from config import supabase

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def dashboard_stats():
    try:
        today = str(date.today())
        week_start = str(date.today() - timedelta(days=7))
        month_start = str(date.today().replace(day=1))

        def sales_in_range(from_dt, to_dt=None):
            q = supabase.table("sales").select("total_amount").gte("created_at", from_dt)
            if to_dt: q = q.lte("created_at", to_dt)
            return q.execute().data

        today_s  = sales_in_range(f"{today}T00:00:00", f"{today}T23:59:59")
        weekly_s = sales_in_range(f"{week_start}T00:00:00")
        monthly_s= sales_in_range(f"{month_start}T00:00:00")
        all_s    = supabase.table("sales").select("total_amount").execute().data

        prods = supabase.table("products").select("*").execute().data
        supps = supabase.table("suppliers").select("id").execute().data
        items = supabase.table("sale_items").select("product_id, product_name, quantity, total_price").execute().data

        low_stock = [p for p in prods if p["stock_quantity"] <= p["low_stock_threshold"]]

        product_totals = {}
        for item in items:
            k = item.get("product_id") or item["product_name"]
            if k not in product_totals:
                product_totals[k] = {"name": item["product_name"], "qty": 0, "revenue": 0}
            product_totals[k]["qty"] += item["quantity"]
            product_totals[k]["revenue"] += float(item.get("total_price") or 0)
        top5 = sorted(product_totals.values(), key=lambda x: x["qty"], reverse=True)[:5]

        daily = []
        for i in range(6, -1, -1):
            d = date.today() - timedelta(days=i)
            ds = str(d)
            ds_data = sales_in_range(f"{ds}T00:00:00", f"{ds}T23:59:59")
            daily.append({"date": ds, "label": d.strftime("%a"),
                          "revenue": sum(s["total_amount"] for s in ds_data),
                          "transactions": len(ds_data)})

        cats = {}
        for p in prods:
            c = p.get("category", "General")
            if c not in cats: cats[c] = {"count": 0, "value": 0}
            cats[c]["count"] += 1
            cats[c]["value"] += p["stock_quantity"] * float(p.get("selling_price", 0))

        return {"success": True, "data": {
            "today": {"revenue": round(sum(s["total_amount"] for s in today_s), 2), "transactions": len(today_s)},
            "weekly_revenue":   round(sum(s["total_amount"] for s in weekly_s), 2),
            "monthly_revenue":  round(sum(s["total_amount"] for s in monthly_s), 2),
            "total_revenue":    round(sum(s["total_amount"] for s in all_s), 2),
            "total_transactions": len(all_s),
            "total_products":   len(prods),
            "low_stock_count":  len(low_stock),
            "total_suppliers":  len(supps),
            "top_products":     top5,
            "daily_chart":      daily,
            "categories":       [{"name": k, **v} for k, v in cats.items()]
        }}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/low-stock")
async def low_stock_alerts():
    try:
        r = supabase.table("products").select("id, name, category, stock_quantity, low_stock_threshold").execute()
        alerts = [p for p in r.data if p["stock_quantity"] <= p["low_stock_threshold"]]
        return {"success": True, "data": alerts, "count": len(alerts)}
    except Exception as e:
        raise HTTPException(500, str(e))
