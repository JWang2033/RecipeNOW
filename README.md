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
# Clone the repository
git clone https://github.com/yourusername/recipenow.git
cd recipenow

# Create venv
python3 -m venv venv

# Activate venv（Mac/Linux）
source venv/bin/activate

# install dependencies
pip install -r requirements.txt

# load
./venv/bin/uvicorn main:app --reload
```

## 📝 File Structure
<!-- tree:start -->
```
.
├── backend
│   └── routers
│       ├── deepseek_router.py
│       ├── generate_rec_router.py
│       ├── scan_router.py
│       └── shopping_list_router.py
├── frontend
├── main.py
├── project_structure.txt
├── README.md
└── requirements.txt

4 directories, 8 files
```
<!-- tree:end -->
