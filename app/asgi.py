from __future__ import annotations

from app.api.auth_v1 import router as auth_router
from app.api.profiles_v1 import router as profiles_router
from app.core.runtime import configure_runtime
from app.core.settings import get_settings
from app.main import app as application


settings = get_settings()
application.include_router(auth_router)
application.include_router(profiles_router)
app = configure_runtime(application, settings)
