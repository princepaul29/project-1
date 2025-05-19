from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from app.models.visitor import Visitor
from app.config.db import get_session

class VisitorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        allowed_paths = {"/", "/search", "/products"}

        if request.url.path in allowed_paths:
            ip = request.client.host
            user_agent = request.headers.get("user-agent", "")
            path = str(request.url.path)

            # Save visitor to DB
            session_gen = get_session()
            session = next(session_gen)
            session.add(Visitor(ip=ip, user_agent=user_agent, path=path))
            session.commit()

        response = await call_next(request)

        return response