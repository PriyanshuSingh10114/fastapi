from pydantic import BaseModel, Field, AnyUrl, field_validator, model_validator, computed_field, EmailStr
from typing import Annotated, Literal, Optional, List
from uuid import UUID
from datetime import datetime

class Seller(BaseModel):
    id: UUID
    name: Annotated[
        str,
        Field(
            min_length=2,
            max_length=60,
            title="Seller Name",
            description="Name of the seller(2-60 chars).",
            examples=["Mi Store", "Apple Store India"],
        )
    ]
    email: EmailStr
    website: AnyUrl

    @field_validator("email",mode="after")
    @classmethod
    def validate_sku_format(cls,value:EmailStr):
        allowed_domains=["mistore.in","hpworld.in"]
        domain=str(value).split("@")[-1].lower()
        if domain not in allowed_domains:
            raise ValueError(f"Seller email domain not allowed: {domain}")
        return value

class DimensionsCM(BaseModel):
    length: Annotated[
        float,
        Field(
            gt=0,
            strict=True,
            description="Length in cm"
        )
    ]

    width: Annotated[
        float,
        Field(
            gt=0,
            strict=True,
            description="Width in cm"
        )
    ]

    height: Annotated[
        float,
        Field(
            gt=0,
            strict=True,
            description="Height in cm"
        )
    ]

class Product(BaseModel):
    id: UUID
    sku: Annotated[
        str, 
        Field(
            min_length=6, 
            max_length=30, 
            title="SKU", 
            description="Stock keeping Unit", 
            examples=["XIAO-359GB-001"]
        ),
    ]

    name: Annotated[
        str,
        Field(
            min_length=3,
            max_length=80,
            title="Product Name",
            description="Readable name of the product",
            examples=["Xiaomi Model Pro","Apple Model X"]
        ),
    ]

    description:Annotated[
        str,
        Field(
            max_length=200,
            description="Short Product Description"
        ),
    ]

    category: Annotated[
        str,
        Field(
            min_length=3,
            max_length=30,
            description="Category like mobiles/laptops/electronics/accessories",
            examples=["mobiles","Laptops"]
        ),
    ]

    brand:Annotated[
        str,
        Field(
            min_length=2,
            max_length=40,
            examples=["Xiaomi","Apple"],
        ),
    ]

    price:Annotated[
        float, 
        Field(
            gt=0,
            strict=(True),
            description="Base Price (INR)"
        )
    ]

    currency: Literal["INR"]="INR"

    discount_percent: Annotated[
        int,
        Field(
            ge=0, 
            le=90,
            description="Discount in percent(0-90)"
        )
    ]=0

    stock:Annotated[
        int,
        Field(
            ge=0,
            description="Available stock(>=0)"
        )
    ]

    is_active:Annotated[
        bool,
        Field(
            description="Is Product active?"
        )
    ]

    rating: Annotated[
        float,
        Field(
            ge=0,
            le=5,
            strict=True,
            description="Rating out of 5"
        )
    ]

    tags:Annotated[
        Optional[List[str]],
        Field(
            default=None,
            description="upto 10 tags"
        )
    ]

    image_urls:Annotated[
        List[AnyUrl],
        Field(
            min_length=1,
            max_length=10,
            description="atleast 1 image url"
        )
    ]

    seller: Seller
    dimenssion_cm: DimensionsCM

    created_time:datetime

    @field_validator("sku",mode="after")
    @classmethod
    def validate_sku_format(cls,value:str):
        if "-" not in value:
            raise ValueError("SKU must have '-'")

        last=value.split("-")[-1]
        if not (len(last)==3 and last.isdigit()):
            raise ValueError("SKU must end with a 3-digit sequence like -234")

        return value    
    

    @model_validator(mode='after')
    def validate_business_rules(cls,model:"Product"):
        if model.stock==0 and model.is_active is True:
            raise ValueError("if stock is 0, is_active must be false")
        if model.discount_percent>0 and model.rating==0:
            raise ValueError("Discounted product must have a rating (rating!=0)")
        return model

    @computed_field
    @property
    def final_price(self)->float:
        return round (self.price*(1-self.discount_percent/100),2)
    
    @computed_field
    @property
    def volume_cm3(self)->float:
        d=self.dimenssion_cm
        return round(d.length*d.width*d.height,2)
    



class SellerUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=60
    )

    email: Optional[EmailStr] = None

    website: Optional[AnyUrl] = None

    @field_validator("email", mode="after")
    @classmethod
    def validate_email_domain(cls, value):
        if value is None:
            return value

        allowed_domains = ["mistore.in", "hpworld.in"]

        domain = str(value).split("@")[-1].lower()

        if domain not in allowed_domains:
            raise ValueError(
                f"Seller email domain not allowed: {domain}"
            )

        return value


class DimensionsCMUpdate(BaseModel):
    length: Optional[float] = Field(
        default=None,
        gt=0,
        strict=True
    )

    width: Optional[float] = Field(
        default=None,
        gt=0,
        strict=True
    )

    height: Optional[float] = Field(
        default=None,
        gt=0,
        strict=True
    )


class ProductUpdate(BaseModel):

    sku: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=30
    )

    name: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=80
    )

    description: Optional[str] = Field(
        default=None,
        max_length=200
    )

    category: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=30
    )

    brand: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=40
    )

    price: Optional[float] = Field(
        default=None,
        gt=0,
        strict=True
    )

    currency: Optional[Literal["INR"]] = None

    discount_percent: Optional[int] = Field(
        default=None,
        ge=0,
        le=90
    )

    stock: Optional[int] = Field(
        default=None,
        ge=0
    )

    is_active: Optional[bool] = None

    rating: Optional[float] = Field(
        default=None,
        ge=0,
        le=5,
        strict=True
    )

    tags: Optional[List[str]] = None

    image_urls: Optional[List[AnyUrl]] = Field(
        default=None,
        min_length=1,
        max_length=10
    )

    seller: Optional[SellerUpdate] = None

    dimenssion_cm: Optional[DimensionsCMUpdate] = None

    @field_validator("sku", mode="after")
    @classmethod
    def validate_sku_format(cls, value):
        if value is None:
            return value

        if "-" not in value:
            raise ValueError("SKU must have '-'")

        last = value.split("-")[-1]

        if not (len(last) == 3 and last.isdigit()):
            raise ValueError(
                "SKU must end with a 3-digit sequence like -234"
            )

        return value