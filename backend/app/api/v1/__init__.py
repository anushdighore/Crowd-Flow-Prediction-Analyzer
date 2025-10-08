# API V1 Router
from fastapi import APIRouter
from .endpoints import csrnet_router, tmtb_router

# Create v1 router
api_router = APIRouter(prefix="/api/v1")

# Include endpoint routers
api_router.include_router(csrnet_router)
api_router.include_router(tmtb_router)

__all__ = ['api_router']
