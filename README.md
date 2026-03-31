<p align="center">
  <img src="icon.png" alt="Mehal Lab Inventory" width="120" />
</p>

<h1 align="center">Mehal Lab Inventory System</h1>

<p align="center">
  <strong>A standalone lab inventory management application for research laboratories</strong><br/>
  Built for the <a href="https://medicine.yale.edu/intmed/digestivediseases/">Yale School of Medicine - Liver Center (Mehal Lab)</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white" alt="SQLite" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black" alt="React 18" />
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey" alt="Platform" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License" />
</p>

---

## Overview

Mehal Lab Inventory is a lightweight, self-contained inventory management system designed for academic research laboratories. It packages a FastAPI backend, SQLite database, and React frontend into a single Windows `.exe` that runs locally - no server infrastructure, no cloud accounts, no IT department needed.

Double-click the executable, your browser opens, and your lab inventory is ready to use.

---

## Features

### Inventory Management
- **Full CRUD operations** - add, edit, withdraw, and remove inventory items
- **Multi-field search** - search across item name, catalog number, vendor, type, and location
- **Sortable columns** - click any column header to sort ascending/descending
- **Type-based filtering** - sidebar filters for Antibody, Bacterial Stock, Cell Line, Chemical, Culture Medium, Assay Kit, Primers, and more
- **Pagination** - handles large inventories efficiently

### Smart Catalog Lookup
- **Local catalog database** - 24 pre-loaded common reagents with instant auto-population
- **Online vendor search** - if not found locally, automatically searches Thermo Fisher, Sigma-Aldrich, and other vendor websites
- **Auto-fills**: item name, vendor, type, price, and storage temperature from catalog number alone

### Alerts and Warnings
- **Low stock alerts** - configurable minimum stock per item with visual warnings
- **Expiration tracking** - expired items highlighted in red with dedicated Alerts dashboard
- **Duplicate detection** - warns when adding an item that already exists in inventory, showing current stock and location

### Multi-User Authentication
- **JWT-based login** - secure token authentication with bcrypt password hashing
- **Role-based display** - PI, Associate Research Scientist, Assistant Professor, and custom roles
- **Activity logging** - tracks all inventory actions (add, edit, withdraw, delete) by user with timestamps

### Data Management
- **CSV export** - one-click export of full inventory for analysis in Excel or R
- **Persistent SQLite database** - data stored locally next to the executable
- **Use/withdraw tracking** - log purpose and amount for each withdrawal

---

## Quick Start

### Option 1: Run the Pre-Built Executable (Windows)

1. Download the latest release from [Releases](../../releases)
2. Extract the zip file
3. Double-click `MehalLabInventory.exe`
4. Browser opens automatically to the inventory app

No Python or other software installation required.

### Option 2: Build from Source

**Prerequisites:** Python 3.10 or later

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/mehal-lab-inventory.git
cd mehal-lab-inventory

# Windows - automated build
build.bat

# macOS / Linux - automated build
chmod +x build.sh
./build.sh
```

The executable will be created in `dist/MehalLabInventory/`.

### Option 3: Run as Python Script (Development)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate.bat       # Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database with seed data
python -m app.seed

# Start the server
python launcher.py
```

Visit `http://127.0.0.1:8000` in your browser.

---

## Default Accounts

| Role                         | Username   | Password   |
|------------------------------|------------|------------|
| PI                           | Mehal      | mehal123   |
| Associate Research Scientist | Arumugam   | as3566     |
| Assistant Professor          | Xinshou    | XO123      |

> **Note:** Change the default passwords and `SECRET_KEY` in `.env` before deploying in a shared environment.

---

## Project Structure

```
mehal-lab-inventory/
|-- app/
|   |-- __init__.py
|   |-- main.py                  # FastAPI application with frontend serving
|   |-- database.py              # SQLAlchemy engine and session management
|   |-- models.py                # ORM models: User, InventoryItem, CatalogReference, ActivityLog
|   |-- schemas.py               # Pydantic request/response validation
|   |-- auth.py                  # JWT authentication and password hashing
|   |-- seed.py                  # Database seeder with initial data
|   |-- routes/
|       |-- __init__.py
|       |-- auth_routes.py       # Login and user endpoints
|       |-- inventory_routes.py  # CRUD, search, alerts, stats, CSV export
|       |-- activity_routes.py   # Activity log endpoints
|       |-- catalog_lookup.py    # Online vendor search for catalog numbers
|-- frontend/
|   |-- index.html               # Self-contained React SPA
|-- launcher.py                  # Entry point: server startup + browser launch
|-- mehal_lab.spec               # PyInstaller build configuration
|-- build.bat                    # Windows build script
|-- build.sh                     # macOS/Linux build script
|-- requirements.txt             # Python dependencies
|-- .env                         # Environment variables (SECRET_KEY, DB path)
|-- icon.ico                     # Application icon (Windows)
|-- icon.png                     # Application icon (source)
|-- README.md
```

---

## API Endpoints

All endpoints require JWT authentication (except login).

| Method | Endpoint                          | Description                        |
|--------|-----------------------------------|------------------------------------|
| POST   | `/api/auth/login`                 | Authenticate and receive JWT token |
| GET    | `/api/auth/me`                    | Get current user info              |
| GET    | `/api/inventory`                  | List/search inventory (paginated)  |
| GET    | `/api/inventory/item/{id}`        | Get single item details            |
| POST   | `/api/inventory`                  | Add new item                       |
| PUT    | `/api/inventory/{id}`             | Update item                        |
| DELETE | `/api/inventory/{id}`             | Soft-delete item                   |
| POST   | `/api/inventory/{id}/use`         | Withdraw quantity from item        |
| GET    | `/api/inventory/check-duplicate`  | Check for existing duplicates      |
| GET    | `/api/inventory/alerts`           | Low stock and expired items        |
| GET    | `/api/inventory/stats`            | Dashboard statistics               |
| GET    | `/api/inventory/export/csv`       | Export full inventory as CSV       |
| GET    | `/api/inventory/catalog/{number}` | Local catalog lookup               |
| GET    | `/api/catalog-online/{number}`    | Online vendor search               |
| GET    | `/api/activity`                   | Activity log (newest first)        |

Interactive API documentation is available at `http://127.0.0.1:8000/docs` when the server is running.

---

## Multi-User Network Access

By default, the server runs on `127.0.0.1` (localhost only). To allow other computers on your lab network to access the same inventory:

1. Open `launcher.py` and change:
   ```python
   HOST = "0.0.0.0"
   ```

2. Rebuild the executable

3. Find the server computer's IP address:
   ```
   ipconfig    # Windows
   ifconfig    # macOS/Linux
   ```

4. Other users open their browser to:
   ```
   http://<SERVER_IP>:8000
   ```

All users share the same database. Changes sync instantly.

---

## Inventory Types

The system supports the following inventory categories, each with a distinct color in the UI:

| Type              | Color   | Example Items                        |
|-------------------|---------|--------------------------------------|
| Antibody          | Blue    | Anti-FLAG M1, HA Tag, FoxP3          |
| Assay Kit         | Purple  | ELISA kits, RT-PCR kits              |
| Bacterial Stock   | Green   | BL21(DE3), DH5alpha, JM109           |
| Cell Line         | Red     | HepG2, HEK293, HeLa                  |
| Chemical          | Amber   | FBS, Pen-Strep, Trypsin              |
| Culture Medium    | Teal    | DMEM, RPMI                            |
| General           | Yellow  | General lab supplies                  |
| Genotyping Primer | Magenta | Custom genotyping primers             |
| Oligo             | Violet  | Custom oligonucleotides               |
| Plasmid           | Cyan    | pGL4.10, expression vectors           |
| RT-PCR Primer     | Emerald | qPCR primers                          |
| Virus             | Pink    | Viral stocks, AAV, lentivirus         |

---

## Technology Stack

| Component     | Technology                                      |
|---------------|------------------------------------------------|
| Backend       | Python 3.10+, FastAPI 0.115, Uvicorn           |
| Database      | SQLAlchemy 2.0 + SQLite (PostgreSQL-compatible) |
| Authentication| JWT (python-jose) + bcrypt (passlib)            |
| Frontend      | React 18, Babel (standalone SPA)                |
| Packaging     | PyInstaller 6.x                                 |
| Online Search | requests library (Thermo Fisher, Sigma-Aldrich) |

---

## Configuration

Environment variables in `.env`:

| Variable                      | Default                              | Description                    |
|-------------------------------|--------------------------------------|--------------------------------|
| `DATABASE_URL`                | `sqlite:///./mehal_lab.db`           | Database connection string     |
| `SECRET_KEY`                  | `mehal-lab-secret-key-2024`          | JWT signing key (change this!) |
| `ALGORITHM`                   | `HS256`                              | JWT algorithm                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480`                                | Token expiry (8 hours)         |

For PostgreSQL (production):
```
DATABASE_URL=postgresql://user:password@localhost:5432/mehal_lab
```

---

## Troubleshooting

| Issue                          | Solution                                                       |
|--------------------------------|----------------------------------------------------------------|
| Port 8000 already in use       | Close existing instance in Task Manager, or change PORT in `launcher.py` |
| Browser does not open          | Manually navigate to `http://127.0.0.1:8000`                  |
| Antivirus blocks the .exe      | Add exception for the MehalLabInventory folder                 |
| Database issues                | Delete `mehal_lab.db` and restart for a fresh database         |
| Online catalog lookup fails    | Requires internet; falls back to manual entry gracefully       |
| Fonts not loading              | First launch needs internet for Google Fonts (cached after)    |
| Second click does not open     | Server is already running; the .exe detects this and reopens browser |

---

## Resetting the Database

To start fresh with a clean database:

1. Stop the server (close the app or end the process in Task Manager)
2. Delete `mehal_lab.db` from the application folder
3. Restart the application. A new database will be created with seed data.

---

## Contributing

Contributions are welcome. To set up a development environment:

```bash
git clone https://github.com/Suyavaran/mehal-lab-inventory.git
cd mehal-lab-inventory
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m app.seed
python launcher.py
```

The server runs at `http://127.0.0.1:8000`. Frontend changes require editing `frontend/index.html` and refreshing the browser.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Acknowledgments

Developed for the [Mehal Lab](https://medicine.yale.edu/intmed/digestivediseases/) at the Yale School of Medicine Liver Center, Section of Digestive Diseases.

Built with [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/), [SQLAlchemy](https://www.sqlalchemy.org/), and [PyInstaller](https://pyinstaller.org/).
