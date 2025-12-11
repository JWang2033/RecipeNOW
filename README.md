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

## 🛠️ Installation

### Prerequisites

#### 1. Python 3.11+
Check if Python is installed:
```bash
python3 --version  # Should show 3.11 or higher
```

#### 2. Node.js 18+ and npm
Check if Node.js and npm are installed:
```bash
node --version  # Should show v18.0.0 or higher
npm --version   # Should show 9.0.0 or higher
```

### Installation Steps

```bash
# ===========================
# 1. Clone Repository
# ===========================
git clone https://github.com/JWang2033/RecipeNOW.git
cd RecipeNOW

# ===========================
# 2. Configure Environment
# ===========================
# Add your Google Cloud credentials
mkdir -p backend/keys
# <-- Place scan-ingredients.json into backend/keys/ -->

# ===========================
# 3. Backend Setup
# ===========================
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# ===========================
# 4. Run Backend
# ===========================
uvicorn main:app --reload
# Backend will run at http://localhost:8000

# ===========================
# 5. Frontend Setup (New Terminal)
# ===========================
cd frontend
npm install
npm run dev
# Frontend will run at http://localhost:5173
```

### ⚠️ Important Notes
- **No database initialization needed!** The database is already set up in the cloud.
- **Do NOT run** `backend/init_db.py` unless you're setting up a new database.
- All team members share the same cloud database.

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
