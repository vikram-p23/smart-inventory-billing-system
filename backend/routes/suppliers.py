from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from datetime import date
from config import supabase

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])

class SupplierCreate(BaseModel):
    name: str
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    notes: Optional[str] = None

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    notes: Optional[str] = None

class PurchaseCreate(BaseModel):
    supplier_id: Optional[str] = None
    product_id: Optional[str] = None
    supplier_name: str
    product_name: str
    quantity: int
    cost_price: float
    purchase_date: Optional[str] = None
    notes: Optional[str] = None

@router.get("/")
async def get_suppliers(search: Optional[str]=Query(None)):
    try:
        q = supabase.table("suppliers").select("*").order("name")
        if search: q = q.ilike("name", f"%{search}%")
        r = q.execute()
        return {"success": True, "data": r.data, "count": len(r.data)}
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/{supplier_id}")
async def get_supplier(supplier_id: str):
    try:
        r = supabase.table("suppliers").select("*").eq("id", supplier_id).single().execute()
        if not r.data: raise HTTPException(404, "Not found")
        return {"success": True, "data": r.data}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/")
async def create_supplier(s: SupplierCreate):
    try:
        r = supabase.table("suppliers").insert(s.model_dump(exclude_none=True)).execute()
        return {"success": True, "data": r.data[0], "message": "Supplier created"}
    except Exception as e: raise HTTPException(500, str(e))

@router.put("/{supplier_id}")
async def update_supplier(supplier_id: str, s: SupplierUpdate):
    try:
        data = s.model_dump(exclude_none=True)
        r = supabase.table("suppliers").update(data).eq("id", supplier_id).execute()
        if not r.data: raise HTTPException(404, "Not found")
        return {"success": True, "data": r.data[0], "message": "Supplier updated"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.delete("/{supplier_id}")
async def delete_supplier(supplier_id: str):
    try:
        supabase.table("suppliers").delete().eq("id", supplier_id).execute()
        return {"success": True, "message": "Supplier deleted"}
    except Exception as e: raise HTTPException(500, str(e))

@router.get("/purchases/all")
async def get_purchases(supplier_id: Optional[str]=Query(None), from_date: Optional[str]=Query(None), to_date: Optional[str]=Query(None)):
    try:
        q = supabase.table("purchases").select("*").order("created_at", desc=True)
        if supplier_id: q = q.eq("supplier_id", supplier_id)
        if from_date: q = q.gte("purchase_date", from_date)
        if to_date: q = q.lte("purchase_date", to_date)
        r = q.execute()
        return {"success": True, "data": r.data, "count": len(r.data)}
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/purchases")
async def create_purchase(p: PurchaseCreate):
    try:
        data = p.model_dump(exclude_none=True)
        if not data.get("purchase_date"): data["purchase_date"] = str(date.today())
        r = supabase.table("purchases").insert(data).execute()
        if p.product_id:
            prod = supabase.table("products").select("stock_quantity").eq("id", p.product_id).single().execute()
            if prod.data:
                new_qty = prod.data["stock_quantity"] + p.quantity
                supabase.table("products").update({"stock_quantity": new_qty}).eq("id", p.product_id).execute()
        return {"success": True, "data": r.data[0], "message": f"Procurement recorded. Stock updated (+{p.quantity})"}
    except Exception as e: raise HTTPException(500, str(e))

@router.delete("/purchases/{purchase_id}")
async def delete_purchase(purchase_id: str):
    try:
        supabase.table("purchases").delete().eq("id", purchase_id).execute()
        return {"success": True, "message": "Purchase deleted"}
    except Exception as e: raise HTTPException(500, str(e))
