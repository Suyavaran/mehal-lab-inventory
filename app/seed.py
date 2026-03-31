"""
Database seeder: populates initial users, catalog reference, and inventory items.
Run with:  python -m app.seed
"""
from app.database import engine, SessionLocal, Base
from app.models import User, InventoryItem, CatalogReference
from app.auth import hash_password


def seed():
    # Create all tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ===================================
        # USERS
        # ===================================
        if db.query(User).count() == 0:
            users = [
                User(
                    username="Mehal",
                    hashed_password=hash_password("mehal123"),
                    full_name="Dr. Mehal",
                    role="PI",
                    email="mehal@yale.edu",
                ),
                User(
                    username="Arumugam",
                    hashed_password=hash_password("as3566"),
                    full_name="Arumugam",
                    role="Associate Research Scientist",
                    email="arumugam@yale.edu",
                ),
                User(
                    username="Xinshou",
                    hashed_password=hash_password("XO123"),
                    full_name="Dr. Xinshou",
                    role="Assistant Professor",
                    email="xinshou@yale.edu",
                ),
            ]
            db.add_all(users)
            db.commit()
            print(f"[OK] Seeded {len(users)} users")
        else:
            print("* Users already exist, skipping")

        # ===================================
        # CATALOG REFERENCE (auto-populate)
        # ===================================
        if db.query(CatalogReference).count() == 0:
            catalog_entries = [
                CatalogReference(catalog_number="9272S", name="Anti-14-3-3 Beta Antibody", inventory_type="Antibody", vendor="Cell Signaling Technology", unit_price=345.00, storage_temp="-20 deg C", species="Rabbit", clonality="Polyclonal"),
                CatalogReference(catalog_number="SC-2005", name="Anti-Bovine IgG", inventory_type="Antibody", vendor="Santa Cruz Biotechnology", unit_price=289.00, storage_temp="-20 deg C", species="Mouse", clonality="Monoclonal"),
                CatalogReference(catalog_number="F3165", name="Anti-FLAG antibody M1", inventory_type="Antibody", vendor="Sigma-Aldrich", unit_price=475.00, storage_temp="-20 deg C", species="Mouse", clonality="Monoclonal"),
                CatalogReference(catalog_number="SC-803", name="Anti-His polyclonal", inventory_type="Antibody", vendor="Santa Cruz Biotechnology", unit_price=305.00, storage_temp="-20 deg C", species="Rabbit", clonality="Polyclonal"),
                CatalogReference(catalog_number="NB100-317", name="Anti-TERT Antibody", inventory_type="Antibody", vendor="Novus Biologicals", unit_price=346.00, storage_temp="-20 deg C", species="Rabbit", clonality="Polyclonal"),
                CatalogReference(catalog_number="EC0114", name="BL21 (DE3)", inventory_type="Bacterial Stock", vendor="Thermo Fisher", unit_price=231.00, storage_temp="-80 deg C", species="E. coli", clonality="N/A"),
                CatalogReference(catalog_number="300-004", name="CD4 (GK1.5)", inventory_type="Antibody", vendor="BioLegend", unit_price=289.00, storage_temp="4 deg C", species="Rat", clonality="Monoclonal"),
                CatalogReference(catalog_number="18265017", name="DH5alpha Competent Cells", inventory_type="Bacterial Stock", vendor="Thermo Fisher", unit_price=494.00, storage_temp="-80 deg C", species="E. coli", clonality="N/A"),
                CatalogReference(catalog_number="F7367", name="Goat anti-rabbit FITC", inventory_type="Antibody", vendor="Sigma-Aldrich", unit_price=205.00, storage_temp="4 deg C", species="Goat", clonality="Polyclonal"),
                CatalogReference(catalog_number="26183", name="HA Tag Antibody", inventory_type="Antibody", vendor="Thermo Fisher", unit_price=10.00, storage_temp="-20 deg C", species="Mouse", clonality="Monoclonal"),
                CatalogReference(catalog_number="14-4776-82", name="Human/Mouse FoxP3 Antibody", inventory_type="Antibody", vendor="eBioscience", unit_price=129.00, storage_temp="4 deg C", species="Rat", clonality="Monoclonal"),
                CatalogReference(catalog_number="L3022", name="JM109 Competent Cells", inventory_type="Bacterial Stock", vendor="Promega", unit_price=195.00, storage_temp="-80 deg C", species="E. coli", clonality="N/A"),
                CatalogReference(catalog_number="200194", name="KRX Competent Cells", inventory_type="Bacterial Stock", vendor="Promega", unit_price=331.00, storage_temp="-80 deg C", species="E. coli", clonality="N/A"),
                CatalogReference(catalog_number="L1001", name="L-Glutamine 200mM", inventory_type="Chemical", vendor="Gibco", unit_price=42.00, storage_temp="4 deg C", species="N/A", clonality="N/A"),
                CatalogReference(catalog_number="T4049", name="Trypsin-EDTA 0.25%", inventory_type="Chemical", vendor="Sigma-Aldrich", unit_price=58.00, storage_temp="-20 deg C", species="N/A", clonality="N/A"),
                CatalogReference(catalog_number="D5796", name="DMEM High Glucose", inventory_type="Chemical", vendor="Sigma-Aldrich", unit_price=32.00, storage_temp="4 deg C", species="N/A", clonality="N/A"),
                CatalogReference(catalog_number="P0781", name="Penicillin-Streptomycin", inventory_type="Chemical", vendor="Sigma-Aldrich", unit_price=28.00, storage_temp="-20 deg C", species="N/A", clonality="N/A"),
                CatalogReference(catalog_number="10270106", name="Fetal Bovine Serum", inventory_type="Chemical", vendor="Gibco", unit_price=450.00, storage_temp="-20 deg C", species="Bovine", clonality="N/A"),
                CatalogReference(catalog_number="CRL-11268", name="HepG2 Cell Line", inventory_type="Cell Line", vendor="ATCC", unit_price=550.00, storage_temp="-196 deg C (LN2)", species="Human", clonality="N/A"),
                CatalogReference(catalog_number="CRL-1573", name="HEK293 Cell Line", inventory_type="Cell Line", vendor="ATCC", unit_price=550.00, storage_temp="-196 deg C (LN2)", species="Human", clonality="N/A"),
                CatalogReference(catalog_number="CRL-2", name="HeLa Cell Line", inventory_type="Cell Line", vendor="ATCC", unit_price=550.00, storage_temp="-196 deg C (LN2)", species="Human", clonality="N/A"),
                CatalogReference(catalog_number="V517A", name="pGL4.10 [luc2] Vector", inventory_type="Plasmid", vendor="Promega", unit_price=395.00, storage_temp="-20 deg C", species="N/A", clonality="N/A"),
                CatalogReference(catalog_number="R0146S", name="EcoRI-HF", inventory_type="Enzyme-Restriction", vendor="New England Biolabs", unit_price=63.00, storage_temp="-20 deg C", species="N/A", clonality="N/A"),
                CatalogReference(catalog_number="R3136S", name="BamHI-HF", inventory_type="Enzyme-Restriction", vendor="New England Biolabs", unit_price=63.00, storage_temp="-20 deg C", species="N/A", clonality="N/A"),
            ]
            db.add_all(catalog_entries)
            db.commit()
            print(f"[OK] Seeded {len(catalog_entries)} catalog entries")
        else:
            print("* Catalog reference already exists, skipping")

        # ===================================
        # INITIAL INVENTORY
        # ===================================
        if db.query(InventoryItem).count() == 0:
            # Get user IDs
            mehal = db.query(User).filter(User.username == "Mehal").first()
            arumugam = db.query(User).filter(User.username == "Arumugam").first()
            xinshou = db.query(User).filter(User.username == "Xinshou").first()

            items = [
                InventoryItem(name="Anti-14-3-3 Beta Antibody", catalog_number="9272S", inventory_type="Antibody", vendor="Cell Signaling Technology", location="Freezer 3 > Shelf 1 > A", position="A1, A2, A3", price=345.00, quantity=50, unit="mL", date_received="2020-05-15", expiration_date="2025-05-15", storage_temp="-20 deg C", min_stock=10, added_by=arumugam.id),
                InventoryItem(name="Anti-Bovine IgG", catalog_number="SC-2005", inventory_type="Antibody", vendor="Santa Cruz Biotechnology", location="Freezer 3 > Shelf 1 > A", position="C2", price=289.00, quantity=2, unit="mL", date_received="2020-04-02", expiration_date="2025-04-02", storage_temp="-20 deg C", min_stock=1, added_by=xinshou.id),
                InventoryItem(name="Anti-FLAG antibody M1", catalog_number="F3165", inventory_type="Antibody", vendor="Sigma-Aldrich", location="Freezer 3 > Shelf 1 > A", position="D2", price=475.00, quantity=200, unit="uL", date_received="2020-01-24", expiration_date="2025-01-24", storage_temp="-20 deg C", min_stock=50, added_by=arumugam.id),
                InventoryItem(name="Anti-His polyclonal", catalog_number="SC-803", inventory_type="Antibody", vendor="Santa Cruz Biotechnology", location="Freezer 3 > Shelf 1 > A", position="D4", price=305.00, quantity=100, unit="uL", date_received="2024-06-12", expiration_date="2026-06-12", storage_temp="-20 deg C", min_stock=25, added_by=mehal.id),
                InventoryItem(name="Anti-TERT Antibody", catalog_number="NB100-317", inventory_type="Antibody", vendor="Novus Biologicals", location="Freezer 1 > Shelf 2 > A", position="A5", price=346.00, quantity=100, unit="uL", date_received="2019-11-18", expiration_date="2024-11-18", storage_temp="-20 deg C", min_stock=25, added_by=arumugam.id, notes="Expired - needs reorder"),
                InventoryItem(name="BL21 (DE3)", catalog_number="EC0114", inventory_type="Bacterial Stock", vendor="Thermo Fisher", location="Freezer 1 > Shelf 3 > F", position="B2", price=231.00, quantity=20, unit="units", date_received="2024-01-10", expiration_date="2026-01-10", storage_temp="-80 deg C", min_stock=5, added_by=xinshou.id),
                InventoryItem(name="CD4 (GK1.5)", catalog_number="300-004", inventory_type="Antibody", vendor="BioLegend", location="Freezer 3 > Shelf 1 > A", position="E1-E9", price=289.00, quantity=1, unit="mL", date_received="2024-03-20", expiration_date="2026-03-20", storage_temp="4 deg C", min_stock=0.5, added_by=xinshou.id),
                InventoryItem(name="DH5alpha Competent Cells", catalog_number="18265017", inventory_type="Bacterial Stock", vendor="Thermo Fisher", location="Freezer 1 > Shelf 3 > F", position="A1-A5", price=494.00, quantity=96, unit="units", date_received="1996-05-25", expiration_date="2001-05-25", storage_temp="-80 deg C", min_stock=20, added_by=mehal.id, notes="Legacy stock"),
                InventoryItem(name="Goat anti-rabbit FITC", catalog_number="F7367", inventory_type="Antibody", vendor="Sigma-Aldrich", location="Freezer 3 > Shelf 1 > A", position="D3", price=205.00, quantity=0.5, unit="mL", date_received="2019-01-30", expiration_date="2024-01-30", storage_temp="4 deg C", min_stock=0.2, added_by=arumugam.id),
                InventoryItem(name="HA Tag Antibody", catalog_number="26183", inventory_type="Antibody", vendor="Thermo Fisher", location="Freezer 1 > Shelf 1 > 1", position="H1", price=10.00, quantity=2, unit="mL", date_received="2020-02-03", expiration_date="2025-02-03", storage_temp="-20 deg C", min_stock=0.5, added_by=mehal.id),
                InventoryItem(name="HepG2 Cell Line", catalog_number="CRL-11268", inventory_type="Cell Line", vendor="ATCC", location="LN2 Tank 1 > Rack 2", position="Box A, Slot 3-5", price=550.00, quantity=3, unit="vials", date_received="2023-09-15", expiration_date="N/A", storage_temp="-196 deg C (LN2)", min_stock=2, added_by=mehal.id, notes="Passage 12-15"),
                InventoryItem(name="EcoRI-HF", catalog_number="R0146S", inventory_type="Enzyme-Restriction", vendor="New England Biolabs", location="Freezer 1 > Shelf 1 > Enzyme Box", position="Slot 3", price=63.00, quantity=5000, unit="units", date_received="2024-08-01", expiration_date="2025-08-01", storage_temp="-20 deg C", min_stock=1000, added_by=xinshou.id),
                InventoryItem(name="DMEM High Glucose", catalog_number="D5796", inventory_type="Chemical", vendor="Sigma-Aldrich", location="Cold Room > Shelf 2", position="Row B", price=32.00, quantity=6, unit="bottles", date_received="2024-11-01", expiration_date="2025-11-01", storage_temp="4 deg C", min_stock=2, added_by=arumugam.id, notes="500mL each"),
                InventoryItem(name="Fetal Bovine Serum", catalog_number="10270106", inventory_type="Chemical", vendor="Gibco", location="Freezer 2 > Shelf 1", position="A1-A4", price=450.00, quantity=4, unit="bottles", date_received="2024-10-20", expiration_date="2026-10-20", storage_temp="-20 deg C", min_stock=2, added_by=xinshou.id, notes="Heat inactivated, 500mL each"),
            ]
            db.add_all(items)
            db.commit()
            print(f"[OK] Seeded {len(items)} inventory items")
        else:
            print("* Inventory items already exist, skipping")

        print("\n[*] Mehal Lab Inventory database seeded successfully!")
        print("   Run server: uvicorn app.main:app --reload --port 8000")
        print("   API docs:   http://localhost:8000/docs\n")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
