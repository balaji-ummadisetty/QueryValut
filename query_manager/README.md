# Query Manager — Production Streamlit App

## Folder Structure

```
query_manager/
├── main.py                   ← Entry point: `streamlit run main.py`
├── requirements.txt
├── .env.example
├── README.md
│
├── config/
│   ├── __init__.py
│   └── settings.py           ← App config, env vars, constants
│
├── database/
│   ├── __init__.py
│   ├── connection.py         ← DB connection pool, get_conn()
│   └── migrations.py         ← Schema creation & migrations
│
├── models/
│   ├── __init__.py
│   ├── user.py               ← User dataclass/model
│   ├── folder.py             ← Folder dataclass/model
│   ├── query.py              ← Query dataclass/model
│   └── version.py            ← QueryVersion dataclass/model
│
├── services/
│   ├── __init__.py
│   ├── auth_service.py       ← Login, register, password hashing
│   ├── folder_service.py     ← CRUD for folders
│   ├── query_service.py      ← CRUD for queries
│   └── version_service.py    ← Version history, diff logic
│
├── ui/
│   ├── __init__.py
│   ├── styles.py             ← All CSS injected into Streamlit
│   ├── components.py         ← Reusable UI components (cards, badges)
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── auth_page.py      ← Login / Register page
│   │   ├── browse_page.py    ← Folder tree + query list
│   │   ├── query_page.py     ← Query detail, edit, version history
│   │   ├── activity_page.py  ← Global activity feed
│   │   ├── search_page.py    ← Full-text search
│   │   └── manage_page.py    ← Folder management
│   └── sidebar.py            ← Sidebar navigation
│
└── utils/
    ├── __init__.py
    ├── diff.py               ← SQL diff computation
    └── helpers.py            ← Date formatting, path building, misc
```

## Setup

```bash
pip install -r requirements.txt
streamlit run main.py
```

Default login: `admin` / `admin123`
