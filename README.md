# RecipeNOW App

## 📖 Description
RecipeNOW is an intelligent recipe suggestion app.
Users simply input the ingredients they want to use, and the app will call the **DeepSeek API** to generate the closest matching recipe. This helps reduce food waste and makes cooking more creative.

---

## ✨ Features
- Input any list of ingredients.
- Automatically generate recipe suggestions using **DeepSeek API**.
- Provide step-by-step cooking instructions.
- Suggest possible variations and tips.

---

## 🛠️ Installation & Startup

### 1. Clone and prepare keys
```bash
git clone https://github.com/yourusername/recipenow.git
cd recipenow
mkdir -p backend/keys
# copy scan-ingredients.json into backend/keys (Google service account)
```

### 2. Backend environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

cp .env.example .env
# Edit .env:
# - Set DEEPSEEK_API_KEY, GCP_PROJECT_ID, GCP_LOCATION, GOOGLE_APPLICATION_CREDENTIALS
# - For local dev keep DATABASE_URL=sqlite:///./data/recipenow.db
#   (or fill MYSQL_* if you’ll use MySQL/Docker)
```

### 3. Database choices
- **SQLite (default):** nothing else to install. On the first run execute
  ```bash
  python - <<'PY'
  from backend.User.database import Base, engine
  import backend.User.models
  Base.metadata.create_all(bind=engine)
  PY
  ```
  (Creates `data/recipenow.db` with `users`, `pantry_items`, `user_preferences`, etc.)
- **MySQL via Docker (optional):**
  ```bash
  docker run --name recipenow-mysql \
    -e MYSQL_DATABASE=recipenow \
    -e MYSQL_USER=user \
    -e MYSQL_PASSWORD=recipenow \
    -e MYSQL_ROOT_PASSWORD=root \
    -p 3309:3306 -d mysql:8
  ```
  Update `.env` with matching `MYSQL_*` values (or set `DATABASE_URL=mysql+pymysql://...`) and rerun the bootstrap script above so tables are created in MySQL.

### 4. Frontend environment
```bash
cd frontend
npm install
cp .env.example .env
# Ensure .env contains:
# VITE_API_BASE_URL=http://127.0.0.1:8000/api
# VITE_PROXY_TARGET=http://127.0.0.1:8000
cd ..
```

### 5. Running locally
```bash
# Terminal 1 (backend)
source venv/bin/activate
uvicorn main:app --reload

# Terminal 2 (frontend)
cd frontend
npm run dev
```
Visit the URL printed by Vite (usually http://localhost:3000). All API calls go through `/api/*` and hit FastAPI on port 8000. If the scan endpoint cannot reach Vertex, it automatically falls back to offline OCR (PIL + pytesseract) so testing continues without cloud access.

### 6. Quick verification checklist
1. Register a user → `POST /api/auth/register` returns 200.
2. Log in → `POST /api/auth/login` returns a JWT; localStorage contains `token`.
3. Preferences page → GET/PUT `/api/preferences/` return 200 and persist diets/allergens/time/difficulty.
4. Pantry page → CRUD endpoints under `/api/pantry/` succeed.
5. Scan page → `/api/scan/ingredients` returns either Vertex data or the fallback OCR result (no frontend error).
6. Recipe/shopping list → `/api/generate/ingredients` and `/api/shopping-list/generate`.

### 7. Automated tests
```bash
source venv/bin/activate
python -m pytest
```
The suite mocks external calls so it runs offline.

## 📝 File Structure
<!-- tree:start -->
```
.
├── backend
│   ├── keys
│   │   └── scan-ingredients.json
│   ├── routers
│   │   ├── __init__.py
│   │   ├── generate_rec_router.py
│   │   ├── scan_router.py
│   │   └── shopping_list_router.py
│   └── User
│       ├── config.py
│       ├── crud
│       ├── database.py
│       ├── models
│       ├── routers
│       ├── schemas
│       └── utils
├── frontend
├── main.py
├── project_structure.txt
├── pytest.ini
├── README.md
├── requirements.txt
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── test_generate_rec_router.py
    ├── test_scan_router.py
    └── test_shopping_list_router.py

12 directories, 17 files
```
<!-- tree:end -->
