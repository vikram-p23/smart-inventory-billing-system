from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
from config import supabase

router = APIRouter(prefix="/api/products", tags=["Products"])

class ProductCreate(BaseModel):
    name: str
    category: str = "General"
    sku: Optional[str] = None
    stock_quantity: int = 0
    cost_price: float
    selling_price: float
    low_stock_threshold: int = 10
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    stock_quantity: Optional[int] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    low_stock_threshold: Optional[int] = None
    description: Optional[str] = None

@router.get("/")
async def get_products(search: Optional[str]=Query(None), category: Optional[str]=Query(None)):
    try:
        query = supabase.table("products").select("*").order("name")
        if search: query = query.ilike("name", f"%{search}%")
        if category: query = query.eq("category", category)
        r = query.execute()
        return {"success": True, "data": r.data, "count": len(r.data)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/low-stock")
async def low_stock():
    try:
        r = supabase.table("products").select("*").execute()
        items = [p for p in r.data if p["stock_quantity"] <= p["low_stock_threshold"]]
        return {"success": True, "data": items, "count": len(items)}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/categories")
async def categories():
    try:
        r = supabase.table("products").select("category").execute()
        cats = sorted(set(p["category"] for p in r.data if p.get("category")))
        return {"success": True, "data": cats}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/{product_id}")
async def get_product(product_id: str):
    try:
        r = supabase.table("products").select("*").eq("id", product_id).single().execute()
        if not r.data: raise HTTPException(404, "Product not found")
        return {"success": True, "data": r.data}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.post("/")
async def create_product(product: ProductCreate):
    try:
        r = supabase.table("products").insert(product.model_dump(exclude_none=True)).execute()
        return {"success": True, "data": r.data[0], "message": "Product created"}
    except Exception as e:
        raise HTTPException(500, str(e))

@router.put("/{product_id}")
async def update_product(product_id: str, product: ProductUpdate):
    try:
        data = product.model_dump(exclude_none=True)
        if not data: raise HTTPException(400, "Nothing to update")
        r = supabase.table("products").update(data).eq("id", product_id).execute()
        if not r.data: raise HTTPException(404, "Product not found")
        return {"success": True, "data": r.data[0], "message": "Product updated"}
    except HTTPException: raise
    except Exception as e: raise HTTPException(500, str(e))

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    try:
        supabase.table("products").delete().eq("id", product_id).execute()
        return {"success": True, "message": "Product deleted"}
    except Exception as e:
        raise HTTPException(500, str(e))
