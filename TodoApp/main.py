from fastapi import FastAPI
from .models import Base
from .database import engine
from .routers import auth, todos, admin, users
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from .utils.main_utils import RatelimitMiddleware, LoggingMiddleware

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

#compacta automaticamente as respostas usando o algoritmo GZip, reduzindo o tamanho da carga útil e melhorando o desempenho
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

#middleware CORS permite ou restringe recursos no seu servidor para serem solicitados de outro domínio.
app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"],
)

#garante que todas as solicitações HTTP sejam redirecionadas automaticamente para HTTPS
#app.add_middleware(HTTPSRedirectMiddleware)

#restringe o número de solicitações que um usuário pode fazer à API dentro de um período de tempo específico
app.add_middleware(RatelimitMiddleware, max_requests=31, window=60)

#registra cada solicitação e resposta
app.add_middleware(LoggingMiddleware)

@app.get("/healthy")
def health_check():
    return {'status': 'healthy'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True )


