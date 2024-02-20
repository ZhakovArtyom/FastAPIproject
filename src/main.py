from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from pydantic import BaseModel
from redis import asyncio as aioredis

from auth.base_config import auth_backend, fastapi_users
from auth.schemas import UserCreate, UserRead
from config import REDIS_HOST, REDIS_PORT
from operations.router import router as router_operation
from tasks.router import router as router_tasks
from pages.router import router as router_pages
from chat.router import router as router_chat

app = FastAPI(
    title="Trading App"
)

class UserInDB(BaseModel):
    username: str
    hashed_password: str

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "hashed_password": "fakehashedpassword"
    }
}

def fake_hash_password(password: str):
    return "fakehashed" + password


@app.post("/token")  # Этот путь не будет включен в схему OpenAPI
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(router_operation)
app.include_router(router_tasks)
app.include_router(router_pages)
app.include_router(router_chat)

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"],
)


@app.on_event("startup")
async def startup_event():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")





















# from typing import Any
# from fastapi import Depends, FastAPI, HTTPException, Request

# app = FastAPI()

# async def get_async_session():
#     print("Получение сессии")
#     session = "session"
#     yield session
#     print("Удаление сессии")

# @app.get("/items")
# async def get_items(session=Depends(get_async_session)):
#     print(session)
#     return [{"id": 1}]

# def pagination_params(limit: int = 10, skip: int = 0):
#     return {"limit": limit, "skip": skip}

# class Paginator:
#     def __init__(self, limit: int = 10, skip: int = 0) -> None:
#         self.limit = limit
#         self.skip = skip

# class AuthGuard:
#     def __init__(self, name) -> None:
#         self.name = name

#     def __call__(self, request: Request) -> Any:
#         if "super_cookie" not in request.cookies:
#             raise HTTPException(status_code=403, detail="ЗАПРЕЩЕНО")
#         return True


# from typing import Annotated

# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from pydantic import BaseModel

# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "fakehashedsecret",
#         "disabled": False,
#     },
#     "alice": {
#         "username": "alice",
#         "full_name": "Alice Wonderson",
#         "email": "alice@example.com",
#         "hashed_password": "fakehashedsecret2",
#         "disabled": True,
#     },
# }

# app = FastAPI()


# def fake_hash_password(password: str):
#     return "fakehashed" + password


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class UserInDB(User):
#     hashed_password: str


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)


# def fake_decode_token(token):
#     # This doesn't provide any security at all
#     # Check the next version
#     user = get_user(fake_users_db, token)
#     return user


# async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user


# async def get_current_active_user(
#     current_user: Annotated[User, Depends(get_current_user)]
# ):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# @app.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")

#     return {"access_token": user.username, "token_type": "bearer"}


# @app.get("/users/me")
# async def read_users_me(
#     current_user: Annotated[User, Depends(get_current_active_user)]
# ):
#     return current_user




# auth_guard_payments = AuthGuard("payments")

# @app.get("/payments", dependencies=[Depends(auth_guard_payments)])
# def get_payments():
#     return "ma payments...."

# @app.get("/subjects_class")
# async def get_subjects_class(pagination_params: Paginator = Depends()):
#     return pagination_params

















# from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles
# from fastapi_cache import FastAPICache
# from fastapi_cache.backends.redis import RedisBackend
# from redis import asyncio as aioredis

# from auth.base_config import auth_backend, fastapi_users
# from auth.schemas import UserCreate, UserRead
# from operations.router import router as router_operation
# from tasks.router import router as router_tasks
# from fastapi.middleware.cors import CORSMiddleware
# from pages.router import router as router_pages
# from chat.router import router as chat_router

# app = FastAPI(
#     title="Trading App"
# )

# app.mount("/static", StaticFiles(directory="static"), name="static")

# app.include_router(
#     fastapi_users.get_auth_router(auth_backend),
#     prefix="/auth",
#     tags=["Auth"],
# )

# app.include_router(
#     fastapi_users.get_register_router(UserRead, UserCreate),
#     prefix="/auth",
#     tags=["Auth"],
# )

# origins = [
#     "http://localhost:8000"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
#     allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
#                    "Authorization"],
# )

# app.include_router(router_operation)
# app.include_router(router_tasks)
# app.include_router(router_pages)
# app.include_router(chat_router)





# @app.on_event("startup")
# async def startup_event():
#     redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")