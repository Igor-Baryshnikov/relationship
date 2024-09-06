import uvicorn
from fastapi import FastAPI

from app.api.endpoints.todo import todo_router
from app.api.endpoints.user import user_router

app = FastAPI()

app.include_router(todo_router)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run(app="main:app")