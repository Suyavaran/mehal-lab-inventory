"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# --- Auth ---
class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: str
    role: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True


# --- Inventory ---
class InventoryItemCreate(BaseModel):
    name: str
    catalog_number: Optional[str] = None
    inventory_type: str
    vendor: Optional[str] = None
    location: Optional[str] = None
    position: Optional[str] = None
    price: Optional[float] = 0.0
    quantity: Optional[float] = 0.0
    unit: Optional[str] = "mL"
    date_received: Optional[str] = None
    expiration_date: Optional[str] = None
    storage_temp: Optional[str] = None
    min_stock: Optional[float] = 0.0
    notes: Optional[str] = ""

class InventoryItemUpdate(BaseModel):
    name: Optional[str] = None
    catalog_number: Optional[str] = None
    inventory_type: Optional[str] = None
    vendor: Optional[str] = None
    location: Optional[str] = None
    position: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    date_received: Optional[str] = None
    expiration_date: Optional[str] = None
    storage_temp: Optional[str] = None
    min_stock: Optional[float] = None
    notes: Optional[str] = None

class InventoryItemResponse(BaseModel):
    id: int
    name: str
    catalog_number: Optional[str]
    inventory_type: str
    vendor: Optional[str]
    location: Optional[str]
    position: Optional[str]
    price: float
    quantity: float
    unit: str
    date_received: Optional[str]
    expiration_date: Optional[str]
    storage_temp: Optional[str]
    min_stock: float
    notes: Optional[str]
    is_active: bool
    added_by: Optional[int]
    added_by_name: Optional[str] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class InventoryListResponse(BaseModel):
    items: List[InventoryItemResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


# --- Use / Withdraw ---
class UseItemRequest(BaseModel):
    amount: float
    purpose: Optional[str] = ""


# --- Catalog ---
class CatalogResponse(BaseModel):
    catalog_number: str
    name: str
    inventory_type: Optional[str]
    vendor: Optional[str]
    unit_price: Optional[float]
    storage_temp: Optional[str]
    species: Optional[str]
    clonality: Optional[str]

    class Config:
        from_attributes = True


# --- Activity Log ---
class ActivityLogResponse(BaseModel):
    id: int
    action_type: str
    action_description: Optional[str]
    item_name: Optional[str]
    item_id: Optional[int]
    detail: Optional[str]
    user_id: Optional[int]
    user_name: Optional[str] = None
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True


# --- Stats ---
class StatsResponse(BaseModel):
    total_items: int
    in_stock: int
    low_stock: int
    expired: int
    total_value: float


# --- Duplicate Check ---
class DuplicateCheckResponse(BaseModel):
    is_duplicate: bool
    existing_item: Optional[InventoryItemResponse] = None
    message: str
