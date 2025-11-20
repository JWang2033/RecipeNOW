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

```bash

# Clone API Keys
mkdir -p backend/keys
#拖入下载的scan-ingredients.json


# Clone the repository
git clone https://github.com/yourusername/recipenow.git
cd recipenow

# Create venv
python3 -m venv venv

# Activate venv（Mac/Linux）
source venv/bin/activate

# install dependencies
./venv/bin/pip install -r requirements.txt
#自己电脑装的pip

# load
./venv/bin/uvicorn main:app --reload
```

## 📝 File Structure
<!-- tree:start -->
```
.
├── backend
│   ├── keys
│   │   └── scan-ingredients.json
│   └── routers
│       ├── __init__.py
│       ├── generate_rec_router.py
│       ├── scan_router.py
│       ├── shopping_list_router.py
│       └── test_api_router.py
├── frontend
├── main.py
├── project_structure.txt
├── README.md
└── requirements.txt

5 directories, 10 files
```
<!-- tree:end -->
