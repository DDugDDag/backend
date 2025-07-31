# app/api/__init__.py
from fastapi import APIRouter
from app.api.endpoints import auth, tashu, route_recommend, users

router = APIRouter()
router.include_router(auth.router, prefix="/api", tags=["auth"])
router.include_router(tashu.router, prefix="/api", tags=["tashu"])
router.include_router(route_recommend.router, prefix="/api", tags=["route"])
router.include_router(users.router, prefix="/api", tags=["users"])