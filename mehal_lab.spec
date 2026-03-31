# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Mehal Lab Inventory System.
Build with:  pyinstaller mehal_lab.spec
"""
import os

# Get the directory where THIS spec file lives
SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

a = Analysis(
    [os.path.join(SPEC_DIR, 'launcher.py')],
    pathex=[SPEC_DIR],
    binaries=[],
    datas=[
        # Include the frontend HTML
        (os.path.join(SPEC_DIR, 'frontend'), 'frontend'),
        # Include .env defaults
        (os.path.join(SPEC_DIR, '.env'), '.'),
    ],
    hiddenimports=[
        # FastAPI + Uvicorn
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        # FastAPI
        'fastapi',
        'fastapi.middleware',
        'fastapi.middleware.cors',
        'starlette',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.responses',
        'starlette.routing',
        'starlette.staticfiles',
        # SQLAlchemy
        'sqlalchemy',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.ext.declarative',
        # Auth
        'jose',
        'jose.jwt',
        'passlib',
        'passlib.handlers',
        'passlib.handlers.bcrypt',
        'bcrypt',
        # Pydantic
        'pydantic',
        'pydantic_settings',
        # App modules
        'app',
        'app.main',
        'app.database',
        'app.models',
        'app.schemas',
        'app.auth',
        'app.seed',
        'app.routes',
        'app.routes.auth_routes',
        'app.routes.inventory_routes',
        'app.routes.activity_routes',
        'app.routes.catalog_lookup',
        # Other
        'dotenv',
        'multipart',
        'requests',
        'urllib3',
        'charset_normalizer',
        'certifi',
        'idna',
        'anyio',
        'anyio._backends',
        'anyio._backends._asyncio',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MehalLabInventory',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=os.path.join(SPEC_DIR, 'icon.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MehalLabInventory',
)
