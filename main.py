from fastapi import FastAPI
# from backend.routers import generate_rec_router, scan_router, shopping_list_router
from backend.routers import test_api_router

from dotenv import load_dotenv
load_dotenv()
import os


app = FastAPI()

# app.include_router(generate_rec_router.router)
# app.include_router(scan_router.router)
# app.include_router(shopping_list_router.router)
app.include_router(test_api_router.router)
