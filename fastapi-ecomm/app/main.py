from fastapi import FastAPI, HTTPException, Query, Path, Depends, Request
from services.products import get_all_products, add_product, remove_product,change_product, load_products 
from schema.product import Product, ProductUpdate
from uuid import uuid4, UUID
from datetime import datetime
from typing import List, Dict

app=FastAPI()

@app.middleware("http")
async def lifecycle(request: Request, call_next):
    print("Before Request")
    response = await call_next(request)
    print("After Request")
    return response

def common_logic():
    print("This is common logic for all endpoints")
    return "Common Logic Executed"

@app.get("/", response_model=Dict)
def root(dep=Depends(common_logic)):
    return {"message":"Welcome to FastAPI E-commerce Application!", "dependency_result": dep}

# @app.get('/products/{id}')
# def get_products(id:int):
#     products=["Brush","Toothpaste","Shampoo","Soap"]
#     return products[id]

# @app.get('/products')
# def get_products():
#     return get_all_products()

# @app.get("/products")
# def list_products(name:str):
#     return name

@app.get("/products", response_model=Dict)
def list_products(
    dep=Depends(load_products),
    name: str | None = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search by Product Name (case insensitive)"
    ),
    sort_by_price: bool = Query(
        default=False,
        description="Sort Products by Price"
    ),
    order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order: asc or desc"
    ),
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Number of items to return"
    ),
    offset: int = Query(
        default=0,
        ge=0,
        description="Pagination Offset",
    ),
):
    #products = get_all_products()
    products = dep

    # Search by name
    if name:
        needle = name.strip().lower()
        products = [
            p for p in products
            if needle in p.get("name", "").lower()
        ]

    if not products:
        raise HTTPException(
            status_code=404,
            detail=f"No product found matching '{name}'"
        )

    # Sort by price
    if sort_by_price:
        products = sorted(
            products,
            key=lambda p: p.get("price", 0),
            reverse=(order == "desc")
        )

    total = len(products)

    # Apply limit
    products = products[offset:offset+limit]

    return {
        "total": total,
        "count": len(products),
        "items": products
    }


@app.get("/products/{product_id}", response_model=Dict)
def get_products_by_id(
    product_id: str = Path(
        ...,
        min_length=36,
        max_length=36,
        description="UUID of the product",
        examples="c47ea245-c4a9-4bff-9dd5-6464f0ebe343"
    )
):
    products = get_all_products()

    for product in products:
        if product["id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found!"
    )

  
@app.post("/products", status_code=201)
def create_product(product: Product):
    product_dict=product.model_dump(mode="json")
    product_dict["id"]=str(uuid4())
    product_dict["created_at"]=datetime.utcnow().isoformat() + "Z"
    try:
        add_product(product_dict)
    except ValueError as e:
        raise HTTPException(status_code=400,detail=str(e))
    return product.model_dump(mode="json")


@app.delete("/products/{product_id}")
def delete_product(
    product_id: UUID = Path(...,description="Product Id")
):
    try:
        res=remove_product(str(product_id))
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.put("/products/{product_id}")
def update_product(
    product_id: UUID = Path(...,description="Product UUID"),
    payload: ProductUpdate=...,
):
    try:
        update_product=change_product(str(product_id),payload.model_dump(mode="json", exclude_unset=True))
        return update_product
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
