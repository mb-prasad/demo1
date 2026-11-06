import json
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, field_validator

app = FastAPI(title="demo1x1 users API")

DATA_FILE = Path(__file__).resolve().parent / "data" / "users.json"
DEVICES_FILE = Path(__file__).resolve().parent / "data" / "devices.json"


class UserCreate(BaseModel):
    name: str
    email: str
    age: Optional[int] = None


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None

    @field_validator("name", "email")
    @classmethod
    def reject_null(cls, value: Optional[str]) -> Optional[str]:
        # name and email are required fields, so they cannot be set to null.
        if value is None:
            raise ValueError("must not be null")
        return value


class User(UserCreate):
    id: int


class DeviceCreate(BaseModel):
    name: str
    type: Optional[str] = None


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None

    @field_validator("name")
    @classmethod
    def reject_null(cls, value: Optional[str]) -> Optional[str]:
        # name is a required field, so it cannot be set to null.
        if value is None:
            raise ValueError("must not be null")
        return value


class Device(DeviceCreate):
    id: int
    user_id: int


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


def load_devices() -> List[dict]:
    """Read all devices from the JSON file. A missing or empty file means no devices."""
    if not DEVICES_FILE.exists():
        return []
    content = DEVICES_FILE.read_text(encoding="utf-8")
    if not content.strip():
        return []
    return json.loads(content)


def save_devices(devices: List[dict]) -> None:
    """Write the full device list back to the JSON file."""
    DEVICES_FILE.parent.mkdir(parents=True, exist_ok=True)
    DEVICES_FILE.write_text(json.dumps(devices, indent=2) + "\n", encoding="utf-8")


def find_index(users: List[dict], user_id: int) -> int:
    for index, user in enumerate(users):
        if user["id"] == user_id:
            return index
    return -1


def find_device_index(devices: List[dict], user_id: int, device_id: int) -> int:
    """Return the index of a device owned by user_id, or -1 if there is none."""
    for index, device in enumerate(devices):
        if device["id"] == device_id and device["user_id"] == user_id:
            return index
    return -1


def require_user(user_id: int) -> None:
    if find_index(load_users(), user_id) == -1:
        raise HTTPException(status_code=404, detail="User not found")


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
    # Deleting a user also removes that user's devices.
    devices = load_devices()
    save_devices([device for device in devices if device["user_id"] != user_id])
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.post(
    "/users/{user_id}/devices",
    response_model=Device,
    status_code=status.HTTP_201_CREATED,
)
def create_device(user_id: int, payload: DeviceCreate) -> dict:
    require_user(user_id)
    devices = load_devices()
    next_id = max((device["id"] for device in devices), default=0) + 1
    device = {"id": next_id, "user_id": user_id, **payload.model_dump()}
    devices.append(device)
    save_devices(devices)
    return device


@app.get("/users/{user_id}/devices", response_model=List[Device])
def list_devices(user_id: int) -> List[dict]:
    require_user(user_id)
    return [device for device in load_devices() if device["user_id"] == user_id]


@app.get("/users/{user_id}/devices/{device_id}", response_model=Device)
def get_device(user_id: int, device_id: int) -> dict:
    require_user(user_id)
    devices = load_devices()
    index = find_device_index(devices, user_id, device_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="Device not found")
    return devices[index]


@app.put("/users/{user_id}/devices/{device_id}", response_model=Device)
def update_device(user_id: int, device_id: int, payload: DeviceUpdate) -> dict:
    require_user(user_id)
    devices = load_devices()
    index = find_device_index(devices, user_id, device_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="Device not found")
    changes = payload.model_dump(exclude_unset=True)
    devices[index].update(changes)
    save_devices(devices)
    return devices[index]


@app.delete(
    "/users/{user_id}/devices/{device_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_device(user_id: int, device_id: int) -> Response:
    require_user(user_id)
    devices = load_devices()
    index = find_device_index(devices, user_id, device_id)
    if index == -1:
        raise HTTPException(status_code=404, detail="Device not found")
    devices.pop(index)
    save_devices(devices)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
