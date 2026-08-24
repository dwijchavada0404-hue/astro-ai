from __future__ import annotations

from app.core.runtime import configure_runtime
from app.core.settings import get_settings
from app.main import app as application


settings = get_settings()
app = configure_runtime(application, settings)
