from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
import uuid
from config import supabase

router = APIRouter(prefix="/api/sales", tags=["Sales"])

class SaleItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float

class SaleCreate(BaseModel):
    customer_name: Optional[str] = "Walk-in Customer"
    items: List[SaleItem]
    discount: float = 0.0
    tax: float = 0.0
    payment_method: str = "cash"
    notes: Optional[str] = None

@router.get("/")
async def get_sales(from_date: Optional[str]=Query(None), to_date: Optional[str]=Query(None), limit: int=Query(50)):
    try:
        q = supabase.table("sales").select("*, sale_items(*)").order("created_at", desc=True).limit(limit)
        if from_date: q = q.gte("created_at", from_date)
        if to_date: q = q.lte("created_at", f"{to_date}T23:59:59")
        r = q.execute()
        return {"success": True, "data": r.data, "count": len(r.data)}
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/today")
async def today_sales():
    try:
        today = str(date.today())
        r = supabase.table("sales").select("*, sale_items(*)").gte("created_at", f"{today}T00:00:00").lte("created_at", f"{today}T23:59:59").order("created_at", desc=True).execute()
        revenue = sum(s["total_amount"] for s in r.data)
        return {"success": True, "data": r.data, "count": len(r.data), "total_revenue": revenue}
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/invoice/{invoice_number}")
async def get_by_invoice(invoice_number: str):
    try:
        r = supabase.table("sales").select("*, sale_items(*)").eq("invoice_number", invoice_number).single().execute()
        if not r.data: raise HTTPException(404, "Invoice not found")
        return {"success": True, "data": r.data}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/{sale_id}")
async def get_sale(sale_id: str):
    try:
        r = supabase.table("sales").select("*, sale_items(*)").eq("id", sale_id).single().execute()
        if not r.data: raise HTTPException(404, "Sale not found")
        return {"success": True, "data": r.data}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/")
async def create_sale(sale: SaleCreate):
    try:
        # Validate stock
        for item in sale.items:
            p = supabase.table("products").select("stock_quantity, name").eq("id", item.product_id).single().execute()
            if not p.data: raise HTTPException(404, f"Product '{item.product_name}' not found")
            if p.data["stock_quantity"] < item.quantity:
                raise HTTPException(400, f"Insufficient stock for '{item.product_name}'. Available: {p.data['stock_quantity']}")

        subtotal = sum(i.quantity * i.unit_price for i in sale.items)
        total = subtotal - sale.discount + sale.tax
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:6].upper()}"

        sale_rec = supabase.table("sales").insert({
            "invoice_number": invoice_number,
            "customer_name": sale.customer_name,
            "subtotal": round(subtotal, 2),
            "discount": round(sale.discount, 2),
            "tax": round(sale.tax, 2),
            "total_amount": round(total, 2),
            "payment_method": sale.payment_method,
            "notes": sale.notes
        }).execute()
        sale_id = sale_rec.data[0]["id"]

        supabase.table("sale_items").insert([{
            "sale_id": sale_id, "product_id": i.product_id,
            "product_name": i.product_name, "quantity": i.quantity, "unit_price": i.unit_price
        } for i in sale.items]).execute()

        for item in sale.items:
            p = supabase.table("products").select("stock_quantity").eq("id", item.product_id).single().execute()
            supabase.table("products").update({"stock_quantity": p.data["stock_quantity"] - item.quantity}).eq("id", item.product_id).execute()

        full = supabase.table("sales").select("*, sale_items(*)").eq("id", sale_id).single().execute()
        return {"success": True, "data": full.data, "invoice_number": invoice_number, "message": "Sale completed"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.delete("/{sale_id}")
async def delete_sale(sale_id: str):
    try:
        supabase.table("sales").delete().eq("id", sale_id).execute()
        return {"success": True, "message": "Sale deleted"}
    except Exception as e: raise HTTPException(500, str(e))
