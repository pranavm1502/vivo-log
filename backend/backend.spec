# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for Vivo-Log backend.

Produces a single-folder bundle at dist/backend/ containing:
- The FastAPI/uvicorn server as a standalone executable
- Alembic migrations for database schema management
- alembic.ini configuration
"""

import os
from pathlib import Path

block_cipher = None
backend_dir = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(backend_dir, 'run_server.py')],
    pathex=[backend_dir],
    binaries=[],
    datas=[
        (os.path.join(backend_dir, 'alembic'), 'alembic'),
        (os.path.join(backend_dir, 'alembic.ini'), '.'),
    ],
    hiddenimports=[
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
        'asyncpg',
        'asyncpg.protocol',
        'sqlalchemy.dialects.postgresql',
        'sqlalchemy.dialects.postgresql.asyncpg',
        'app',
        'app.main',
        'app.config',
        'app.database',
        'app.models',
        'app.models.colony',
        'app.models.study',
        'app.routers',
        'app.routers.colony',
        'app.routers.studies',
        'app.routers.analytics',
        'app.routers.export',
        'psycopg2',
        'openpyxl',
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
    name='backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=True,
    target_arch=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='backend',
)
