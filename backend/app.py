"""
RetailOS — FastAPI Backend
"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
load_dotenv()

from routes import products_router, suppliers_router, sales_router, chatbot_router, dashboard_router

app = FastAPI(title="RetailOS API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")

origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000").split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

@app.exception_handler(Exception)
async def global_err(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})

app.include_router(dashboard_router)
app.include_router(products_router)
app.include_router(suppliers_router)
app.include_router(sales_router)
app.include_router(chatbot_router)

@app.get("/")
async def root(): return {"status": "online", "service": "RetailOS API", "docs": "/docs"}

@app.get("/health")
async def health(): return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", 8000)),
                reload=os.environ.get("APP_ENV") == "development")
