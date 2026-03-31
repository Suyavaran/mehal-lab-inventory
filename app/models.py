"""
SQLAlchemy ORM Models for Mehal Lab Inventory System.
"""
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # PI, Associate Research Scientist, etc.
    email = Column(String(120), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    inventory_items = relationship("InventoryItem", back_populates="added_by_user")
    activity_logs = relationship("ActivityLog", back_populates="user")


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    catalog_number = Column(String(50), index=True)
    inventory_type = Column(String(50), nullable=False, index=True)
    vendor = Column(String(150))
    location = Column(String(200))
    position = Column(String(100))
    price = Column(Float, default=0.0)
    quantity = Column(Float, default=0.0)
    unit = Column(String(20), default="mL")
    date_received = Column(String(20))
    expiration_date = Column(String(20))
    storage_temp = Column(String(30))
    min_stock = Column(Float, default=0.0)
    notes = Column(Text, default="")
    is_active = Column(Boolean, default=True)  # Soft delete
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Foreign key to user who added it
    added_by = Column(Integer, ForeignKey("users.id"))
    added_by_user = relationship("User", back_populates="inventory_items")

    # Full-text search index (for PostgreSQL, use pg_trgm; for SQLite this helps)
    __table_args__ = (
        Index("ix_inventory_search", "name", "catalog_number", "vendor", "inventory_type"),
    )


class CatalogReference(Base):
    """
    Reference catalog for auto-populating item details by catalog number.
    """
    __tablename__ = "catalog_reference"

    id = Column(Integer, primary_key=True, index=True)
    catalog_number = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    inventory_type = Column(String(50))
    vendor = Column(String(150))
    unit_price = Column(Float, default=0.0)
    storage_temp = Column(String(30))
    species = Column(String(50))
    clonality = Column(String(30))


class ActivityLog(Base):
    """
    Tracks all inventory actions: add, edit, use/withdraw, delete.
    """
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(String(20), nullable=False)  # add, edit, use, delete
    action_description = Column(String(100))
    item_name = Column(String(200))
    item_id = Column(Integer)
    detail = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="activity_logs")
