from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from fastapi import Request, status, HTTPException
import time
import logging
from starlette.responses import Response

logger = logging.getLogger("my_logger")

#Implementado
class RatelimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, max_requests: int, window:int):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window
        self.requests = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host #type: ignore
        current_time = time.time()

        if client_ip not in self.requests:
            self.requests[client_ip] = []

        self.requests[client_ip] = [timestamp for timestamp in self.requests[client_ip] if timestamp > current_time - self.window]

        if len(self.requests[client_ip]) >= self.max_requests:
            return JSONResponse(status_code=status.HTTP_429_TOO_MANY_REQUESTS, content={"error": "Too many requests"})
        
        self.requests[client_ip].append(current_time)
        return await call_next(request)
    
#lida com autenticação verificando tokens ou credenciais antes que as solicitações cheguem ao endpoint. 
# Classe não implementado 
# para implementar ir no arquivo main na raiz do projeto e adcionar middleware-> app.add_middleware(AuthMiddleware)
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        token = request.headers.get("Authorization")
        if not token or token != "Bearer valid-token":
            return PlainTextResponse(status_code=status.HTTP_401_UNAUTHORIZED, content="Unauthorized")
        return await call_next(request)
    
#registra cada solicitação e resposta
#Implementado
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
        logger.info(f"Request: {request.method} {request.url}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
