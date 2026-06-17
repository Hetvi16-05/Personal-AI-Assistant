import sys
import os

# Add the backend directory to sys.path so the 'app' module can be imported correctly by Vercel
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app

# Vercel serverless functions receive requests prefixed with /api.
# This middleware strips the "/api" prefix so that FastAPI routes (like /auth/login) match correctly.
class StripApiPrefixMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            path = scope.get("path", "")
            if path.startswith("/api"):
                scope["path"] = path[4:]
        await self.app(scope, receive, send)

app = StripApiPrefixMiddleware(app)
