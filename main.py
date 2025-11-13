import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from database import create_document, get_documents, db

app = FastAPI(title="Urban Wheel Pottery API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactMessageIn(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=2000)


# Sample product catalog (used for demo/catalog display)
# Slugs should be unique
SAMPLE_PRODUCTS = [
    {
        "slug": "terra-mug",
        "title": "Terra Mug",
        "description": "Hand-thrown stoneware mug with a warm terracotta glaze.",
        "price": 28.0,
        "type": "mug",
        "image": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "slug": "olive-bowl",
        "title": "Olive Bowl",
        "description": "Muted olive glaze with a subtle matte finish.",
        "price": 34.0,
        "type": "bowl",
        "image": "https://images.unsplash.com/photo-1533321942807-08e8a5f1a3f9?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "slug": "beige-plate",
        "title": "Beige Dinner Plate",
        "description": "Warm beige plate with light speckle texture.",
        "price": 42.0,
        "type": "plate",
        "image": "https://images.unsplash.com/photo-1549880338-65ddcdfd017b?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "slug": "clay-vase",
        "title": "Clay Vase",
        "description": "Elegant tall vase inspired by natural forms.",
        "price": 68.0,
        "type": "vase",
        "image": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "slug": "wheel-mug",
        "title": "Wheel Mug",
        "description": "Classic wheel-thrown mug with ergonomic handle.",
        "price": 26.0,
        "type": "mug",
        "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "slug": "sand-bowl",
        "title": "Sand Bowl",
        "description": "Neutral sand-toned bowl for everyday use.",
        "price": 30.0,
        "type": "bowl",
        "image": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "slug": "horizon-plate",
        "title": "Horizon Plate",
        "description": "Wide rim plate with horizon gradient glaze.",
        "price": 48.0,
        "type": "plate",
        "image": "https://images.unsplash.com/photo-1515543237350-b3eea1ec8082?q=80&w=1600&auto=format&fit=crop",
    },
    {
        "slug": "urban-vase",
        "title": "Urban Vase",
        "description": "Minimalist vase with soft clay brown finish.",
        "price": 72.0,
        "type": "vase",
        "image": "https://images.unsplash.com/photo-1512203492609-8f7f6db6c9f9?q=80&w=1600&auto=format&fit=crop",
    },
]


@app.get("/")
def read_root():
    return {"brand": "Urban Wheel Pottery", "message": "API running"}


@app.get("/api/products")
def list_products(type: Optional[str] = None, minPrice: Optional[float] = None, maxPrice: Optional[float] = None):
    products = SAMPLE_PRODUCTS
    if type:
        products = [p for p in products if p["type"].lower() == type.lower()]
    if minPrice is not None:
        products = [p for p in products if p["price"] >= float(minPrice)]
    if maxPrice is not None:
        products = [p for p in products if p["price"] <= float(maxPrice)]
    return {"items": products}


@app.get("/api/products/{slug}")
def get_product(slug: str):
    for p in SAMPLE_PRODUCTS:
        if p["slug"] == slug:
            return p
    raise HTTPException(status_code=404, detail="Product not found")


@app.post("/api/contact")
def submit_contact(payload: ContactMessageIn):
    """Accept contact form submission and store in database if available"""
    stored = False
    try:
        data = payload.model_dump()
        _id = create_document("contactmessage", data)
        stored = True
        return {"success": True, "stored": stored, "id": _id}
    except Exception as e:
        # Database might not be available; still accept submission
        return {"success": True, "stored": stored, "note": "Saved without DB", "error": str(e)[:120]}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
