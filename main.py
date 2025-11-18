from fastapi import FastAPI
from backend.routers import generate_rec_router, scan_router, shopping_list_router

app = FastAPI()

# 注册各个模块的路由
app.include_router(generate_rec_router.router)
app.include_router(scan_router.router)
app.include_router(shopping_list_router.router)
