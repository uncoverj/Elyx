from .start import router as start_router
from .search import router as search_router
from .profile import router as profile_router
from .settings import router as settings_router
from .matches import router as matches_router
from .premium import router as premium_router

routers = [start_router, search_router, profile_router, settings_router, matches_router, premium_router]
