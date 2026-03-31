"""
Inventory routes: CRUD, search, alerts, use/withdraw, CSV export, catalog auto-populate.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import Optional
from datetime import date
import csv
import io

from app.database import get_db
from app.models import User, InventoryItem, CatalogReference, ActivityLog
from app.schemas import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse,
    InventoryListResponse, UseItemRequest, CatalogResponse,
    StatsResponse, DuplicateCheckResponse,
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])


# --- Helper: log activity ---
def log_activity(db: Session, action_type: str, description: str,
                 item_name: str, item_id: int, detail: str, user_id: int):
    log = ActivityLog(
        action_type=action_type,
        action_description=description,
        item_name=item_name,
        item_id=item_id,
        detail=detail,
        user_id=user_id,
    )
    db.add(log)
    db.commit()


# --- Helper: build response with user name ---
def item_to_response(item: InventoryItem, db: Session) -> dict:
    data = {
        "id": item.id,
        "name": item.name,
        "catalog_number": item.catalog_number,
        "inventory_type": item.inventory_type,
        "vendor": item.vendor,
        "location": item.location,
        "position": item.position,
        "price": item.price or 0.0,
        "quantity": item.quantity or 0.0,
        "unit": item.unit or "mL",
        "date_received": item.date_received,
        "expiration_date": item.expiration_date,
        "storage_temp": item.storage_temp,
        "min_stock": item.min_stock or 0.0,
        "notes": item.notes,
        "is_active": item.is_active,
        "added_by": item.added_by,
        "added_by_name": None,
        "created_at": item.created_at,
        "updated_at": item.updated_at,
    }
    if item.added_by:
        user = db.query(User).filter(User.id == item.added_by).first()
        if user:
            data["added_by_name"] = user.full_name
    return data


# ==============================================
# LIST / SEARCH INVENTORY
# ==============================================
@router.get("", response_model=InventoryListResponse)
def list_inventory(
    search: Optional[str] = Query(None, description="Search name, catalog#, vendor, type, location"),
    inventory_type: Optional[str] = Query(None, description="Filter by type (comma-separated)"),
    sort_by: Optional[str] = Query("name", description="Sort field"),
    sort_dir: Optional[str] = Query("asc", description="asc or desc"),
    page: int = Query(1, ge=1),
    per_page: int = Query(15, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List inventory items with search, filtering, sorting, and pagination."""
    query = db.query(InventoryItem).filter(InventoryItem.is_active == True)

    # Search across multiple fields
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                InventoryItem.name.ilike(search_term),
                InventoryItem.catalog_number.ilike(search_term),
                InventoryItem.vendor.ilike(search_term),
                InventoryItem.inventory_type.ilike(search_term),
                InventoryItem.location.ilike(search_term),
            )
        )

    # Type filter (supports multiple comma-separated types)
    if inventory_type:
        types = [t.strip() for t in inventory_type.split(",")]
        query = query.filter(InventoryItem.inventory_type.in_(types))

    # Sorting
    sort_column = getattr(InventoryItem, sort_by, InventoryItem.name)
    if sort_dir == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Pagination
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    total_pages = (total + per_page - 1) // per_page

    return InventoryListResponse(
        items=[item_to_response(item, db) for item in items],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


# ==============================================
# GET SINGLE ITEM
# ==============================================
@router.get("/item/{item_id}", response_model=InventoryItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id, InventoryItem.is_active == True
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item_to_response(item, db)


# ==============================================
# ADD NEW ITEM (with duplicate warning)
# ==============================================
@router.post("", response_model=InventoryItemResponse)
def add_item(
    item_data: InventoryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new inventory item. Returns the created item."""
    new_item = InventoryItem(
        name=item_data.name,
        catalog_number=item_data.catalog_number,
        inventory_type=item_data.inventory_type,
        vendor=item_data.vendor,
        location=item_data.location,
        position=item_data.position,
        price=item_data.price,
        quantity=item_data.quantity,
        unit=item_data.unit,
        date_received=item_data.date_received,
        expiration_date=item_data.expiration_date,
        storage_temp=item_data.storage_temp,
        min_stock=item_data.min_stock,
        notes=item_data.notes,
        added_by=current_user.id,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    log_activity(db, "add", "added", new_item.name, new_item.id,
                 f"Qty: {new_item.quantity} {new_item.unit}", current_user.id)

    return item_to_response(new_item, db)


# ==============================================
# CHECK FOR DUPLICATES
# ==============================================
@router.get("/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate(
    catalog_number: Optional[str] = None,
    name: Optional[str] = None,
    exclude_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check if an item with same catalog# or name already exists."""
    query = db.query(InventoryItem).filter(InventoryItem.is_active == True)
    if exclude_id:
        query = query.filter(InventoryItem.id != exclude_id)

    existing = None
    if catalog_number:
        existing = query.filter(
            func.lower(InventoryItem.catalog_number) == catalog_number.lower()
        ).first()
    if not existing and name:
        existing = query.filter(
            func.lower(InventoryItem.name) == name.lower()
        ).first()

    if existing:
        return DuplicateCheckResponse(
            is_duplicate=True,
            existing_item=item_to_response(existing, db),
            message=f'"{existing.name}" (Cat# {existing.catalog_number}) already exists '
                    f'at {existing.location} with {existing.quantity} {existing.unit} remaining.',
        )
    return DuplicateCheckResponse(is_duplicate=False, message="No duplicates found.")


# ==============================================
# UPDATE ITEM
# ==============================================
@router.put("/{item_id}", response_model=InventoryItemResponse)
def update_item(
    item_id: int,
    item_data: InventoryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id, InventoryItem.is_active == True
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)

    log_activity(db, "edit", "updated", item.name, item.id,
                 "Updated details", current_user.id)

    return item_to_response(item, db)


# ==============================================
# DELETE ITEM (soft delete)
# ==============================================
@router.delete("/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id, InventoryItem.is_active == True
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item.is_active = False
    db.commit()

    log_activity(db, "delete", "removed", item.name, item.id, "", current_user.id)

    return {"message": f"{item.name} removed from inventory"}


# ==============================================
# USE / WITHDRAW
# ==============================================
@router.post("/{item_id}/use", response_model=InventoryItemResponse)
def use_item(
    item_id: int,
    use_data: UseItemRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Withdraw/use a quantity from an inventory item."""
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id, InventoryItem.is_active == True
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if use_data.amount > item.quantity:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot withdraw {use_data.amount} {item.unit}. "
                   f"Only {item.quantity} {item.unit} available.",
        )

    item.quantity = max(0, item.quantity - use_data.amount)
    db.commit()
    db.refresh(item)

    detail = f"{use_data.amount} {item.unit}"
    if use_data.purpose:
        detail += f" for {use_data.purpose}"

    log_activity(db, "use", "withdrew", item.name, item.id, detail, current_user.id)

    # Return item with low-stock warning in notes if applicable
    response = item_to_response(item, db)
    if item.min_stock > 0 and item.quantity <= item.min_stock:
        response["_low_stock_warning"] = (
            f"Low stock: {item.quantity} {item.unit} remaining "
            f"(minimum: {item.min_stock} {item.unit}). Consider reordering."
        )
    return response


# ==============================================
# ALERTS -- Low stock + Expired
# ==============================================
@router.get("/alerts", response_model=dict)
def get_alerts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get low stock and expired item alerts."""
    active_items = db.query(InventoryItem).filter(InventoryItem.is_active == True).all()
    today = date.today().isoformat()

    low_stock = []
    expired = []

    for item in active_items:
        if item.min_stock and item.min_stock > 0 and item.quantity <= item.min_stock:
            low_stock.append(item_to_response(item, db))
        if (item.expiration_date and item.expiration_date != "N/A"
                and item.expiration_date < today):
            expired.append(item_to_response(item, db))

    return {
        "low_stock": low_stock,
        "expired": expired,
        "low_stock_count": len(low_stock),
        "expired_count": len(expired),
    }


# ==============================================
# STATS -- Dashboard numbers
# ==============================================
@router.get("/stats", response_model=StatsResponse)
def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    active_items = db.query(InventoryItem).filter(InventoryItem.is_active == True).all()
    today = date.today().isoformat()

    total = len(active_items)
    in_stock = sum(1 for i in active_items if i.quantity > 0)
    low_stock = sum(1 for i in active_items
                    if i.min_stock and i.min_stock > 0 and i.quantity <= i.min_stock)
    expired = sum(1 for i in active_items
                  if i.expiration_date and i.expiration_date != "N/A"
                  and i.expiration_date < today)
    total_value = sum(i.price or 0 for i in active_items)

    return StatsResponse(
        total_items=total,
        in_stock=in_stock,
        low_stock=low_stock,
        expired=expired,
        total_value=total_value,
    )


# ==============================================
# EXPORT CSV
# ==============================================
@router.get("/export/csv")
def export_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Export all active inventory items as CSV."""
    items = db.query(InventoryItem).filter(InventoryItem.is_active == True).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "ID", "Name", "Catalog Number", "Type", "Vendor", "Location", "Position",
        "Price", "Quantity", "Unit", "Date Received", "Expiration Date",
        "Storage Temp", "Min Stock", "Notes",
    ])
    for item in items:
        writer.writerow([
            item.id, item.name, item.catalog_number, item.inventory_type,
            item.vendor, item.location, item.position, item.price,
            item.quantity, item.unit, item.date_received, item.expiration_date,
            item.storage_temp, item.min_stock, item.notes,
        ])

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=mehal_lab_inventory_{date.today()}.csv"},
    )


# ==============================================
# CATALOG LOOKUP (auto-populate)
# ==============================================
@router.get("/catalog/{catalog_number}", response_model=CatalogResponse)
def lookup_catalog(
    catalog_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Look up catalog reference to auto-populate item details."""
    ref = db.query(CatalogReference).filter(
        func.lower(CatalogReference.catalog_number) == catalog_number.lower()
    ).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Catalog number not found in reference database")
    return ref
