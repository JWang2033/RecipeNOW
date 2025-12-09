from fastapi import FastAPI

from backend.routers import generate_rec_router, scan_router, shopping_list_router
from backend.User.routers import pantry_router, preferences_router, user_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.include_router(generate_rec_router.router)
app.include_router(scan_router.router)
app.include_router(shopping_list_router.router)
app.include_router(user_router.router)
app.include_router(preferences_router.router)
app.include_router(pantry_router.router)
