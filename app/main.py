from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Any

from app.db import mysql_sync
import app.sql as SQL

app = FastAPI(title="FastAPI + MySQL (Sync, PyMySQL) - Port 3307")

# --- App lifecycle ---
@app.on_event("startup")
def on_startup():
    mysql_sync.connect()
    mysql_sync.execute("SELECT 1")

@app.on_event("shutdown")
def on_shutdown():
    mysql_sync.close()

# --- Health ---
@app.get("/")
def root() :
    return {"message": "OK: FastAPI + MySQL (sync, 3307)"}

# --- Users: List ---
@app.get("/users")
def list_users() :
    cur = mysql_sync.execute(SQL.SELECT_USERS)
    rows = cur.fetchall()
    result = []
    for r in rows:
        created_at = r[3].isoformat() if r[3] else None
        result.append({"id": r[0], "username": r[1], "age": r[2], "created_at": created_at})
    return result

# --- Users: Get by ID ---
@app.get("/users/{user_id}")
def get_user(user_id: int) :
    cur = mysql_sync.execute(SQL.SELECT_USER_BY_ID, (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "User not found")
    return {
        "id": row[0],
        "username": row[1],
        "age": row[2],
        "created_at": row[3].isoformat() if row[3] else None,
    }

# --- Users: Create ---
@app.post("/users", status_code=201)
def create_user(payload: Dict[str, Any] = Body(...)) :
    try:
        username = str(payload.get("username", "")).strip()
        age = int(payload.get("age"))
    except Exception:
        raise HTTPException(400, "Invalid body: require username(str) and age(int)")

    if not username:
        raise HTTPException(400, "username required")

    cur = mysql_sync.execute(SQL.INSERT_USER, (username, age))
    # mysql_sync가 autocommit이 아니면 아래 한 줄 필요:
    # mysql_sync.commit()

    user_id = cur.lastrowid
    cur = mysql_sync.execute(SQL.SELECT_USER_BY_ID, (user_id,))
    row = cur.fetchone()
    return {
        "id": row[0],
        "username": row[1],
        "age": row[2],
        "created_at": row[3].isoformat() if row[3] else None,
    }

# --- Users: Update ---
@app.put("/users/{user_id}")
def update_user(user_id: int, payload: Dict[str, Any] = Body(...)) :
    try:
        username = str(payload.get("username", "")).strip()
        age = int(payload.get("age"))
    except Exception:
        raise HTTPException(400, "Invalid body: require username(str) and age(int)")

    if not username:
        raise HTTPException(400, "username required")

    mysql_sync.execute(SQL.UPDATE_USER_BY_ID, (username, age, user_id))
    # mysql_sync.commit()

    cur = mysql_sync.execute(SQL.SELECT_USER_BY_ID, (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "User not found")
    return {
        "id": row[0],
        "username": row[1],
        "age": row[2],
        "created_at": row[3].isoformat() if row[3] else None,
    }

# --- Users: Delete ---
@app.delete("/users/{user_id}")
def delete_user(user_id: int) :
    mysql_sync.execute(SQL.DELETE_USER_BY_ID, (user_id,))
    # mysql_sync.commit()
    return {"message": f"deleted {user_id}"}
