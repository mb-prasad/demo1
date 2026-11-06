# demo1x1

A minimal FastAPI app with user CRUD endpoints. Users are stored in `data/users.json`, which is read and written on every request.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

The API is then served at http://127.0.0.1:8000, and interactive docs are at http://127.0.0.1:8000/docs.

## Endpoints

| Method | Path             | Description                                      | Success |
|--------|------------------|--------------------------------------------------|---------|
| POST   | `/users`         | Create a user (`name`, `email`, optional `age`)  | 201     |
| GET    | `/users`         | List all users                                   | 200     |
| GET    | `/users/{id}`    | Get one user                                     | 200     |
| PUT    | `/users/{id}`    | Update any of `name`, `email`, `age`             | 200     |
| DELETE | `/users/{id}`    | Delete a user                                    | 204     |

Unknown user ids return `404`.

Example:

```bash
curl -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ada", "email": "ada@example.com", "age": 36}'
```

### Devices

Each user can own devices. Device endpoints are nested under the user:

| Method | Path                                  | Description                                          | Success |
|--------|---------------------------------------|------------------------------------------------------|---------|
| POST   | `/users/{id}/devices`                 | Create a device (`name`, optional `type`)            | 201     |
| GET    | `/users/{id}/devices`                 | List that user's devices                             | 200     |
| GET    | `/users/{id}/devices/{device_id}`     | Get one device                                       | 200     |
| PUT    | `/users/{id}/devices/{device_id}`     | Update any of `name`, `type`                         | 200     |
| DELETE | `/users/{id}/devices/{device_id}`     | Delete a device                                      | 204     |

A device has an integer `id` and a `user_id` taken from the path. Unknown user ids return `404` with detail `User not found`. Unknown device ids, or devices that belong to a different user, return `404` with detail `Device not found`. Deleting a user also deletes that user's devices.

Example:

```bash
curl -X POST http://127.0.0.1:8000/users/1/devices \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "type": "computer"}'
```

## Data files

`data/users.json` holds a JSON list of users. A missing or empty file is treated as an empty list.

`data/devices.json` holds a JSON list of devices, each with `id`, `user_id`, `name`, and `type`. A missing or empty file is treated as an empty list.
