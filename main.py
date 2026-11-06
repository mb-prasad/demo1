import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel

app = FastAPI(title="demo1x1 users API")

DATA_FILE = Path(__file__).resolve().parent / "data" / "users.json"


class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None


class User(UserCreate):
    id: int


def load_users() -> List[dict]:
    """Read all users from the JSON file. A missing or empty file means no users."""
    if not DATA_FILE.exists():
        return []
    content = DATA_FILE.read_text(encoding="utf-8")
    if not content.strip():
        return []
    return json.loads(content)


def save_users(users: List[dict]) -> None:
    """Write the full user list back to the JSON file."""
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(users, indent=2) + "\n", encoding="utf-8")


def find_index(users: List[dict], user_id: int) -> int:
    for index, user in enumerate(users):
        if user["id"] == user_id:
            return index
    return -1


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> dict:
    users = load_users()
    next_id = max((user["id"] for user in users), default=0) + 1
    user = {"id": next_id, **payload.model_dump()}
    users.append(user)
    save_users(users)
    return user


@app.get("/users", response_model=List[User])
def list_users() -> List[dict]:
    return load_users()


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int) -> dict:
    users = load_users()
    index = find_index(users, user_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="User not found")
    return users[index]


@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, payload: UserUpdate) -> dict:
    users = load_users()
    index = find_index(users, user_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="User not found")
    changes = payload.model_dump(exclude_unset=True)
    users[index].update(changes)
    save_users(users)
    return users[index]


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> Response:
    users = load_users()
    index = find_index(users, user_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="User not found")
    users.pop(index)
    save_users(users)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
