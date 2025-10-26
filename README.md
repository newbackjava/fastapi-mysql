# FastAPI + MySQL (Sync, PyMySQL) — 사용 설명서 (README)

이 문서는 첨부된 코드로 **동기 방식(PyMySQL) MySQL 연결**을 사용하는 **FastAPI** 서버를 설치·실행·테스트하는 전 과정을 정리합니다.
(스크린샷처럼 `uvicorn app.main:app --reload` 로 실행하는 흐름을 기준으로 설명합니다.)

---

## 1) 프로젝트 개요

* **프레임워크**: FastAPI
* **DB 드라이버**: PyMySQL (동기)
* **주요 기능**

  * `/` 헬스체크
  * `/users` 사용자 목록 조회 / 생성
  * `/users/{user_id}` 사용자 단건 조회 / 수정 / 삭제
* **DB 스키마**

  * `users(id, username, age, created_at)`

---

## 2) 권장 디렉터리 구조

현재 코드에는 `from app.db import mysql_sync`, `import app.sql as SQL` 임포트가 보입니다. 아래처럼 **모듈을 분리**하면 명확하고 유지보수가 쉽습니다.

```
fastapi-mysql/
├─ app/
│  ├─ __init__.py
│  ├─ db.py        # MySQLSync 클래스 및 인스턴스(mysql_sync)
│  ├─ sql.py       # CREATE/SELECT/INSERT/UPDATE/DELETE 쿼리 상수
│  └─ main.py      # FastAPI 엔드포인트 (app 객체)
├─ .env            # 환경변수 (선택)
├─ requirements.txt
└─ README.md
```

> 만약 **하나의 파일**에 모두 포함해도 동작은 하지만, 임포트 경로를 맞추기 위해선 위 구조처럼 분리하는 것을 권장합니다.

---

## 3) 의존성 설치

### (1) 가상환경 생성 및 활성화

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### (2) 패키지 설치

`requirements.txt` 예시:

```txt
fastapi>=0.110
uvicorn[standard]>=0.29
PyMySQL>=1.1
python-dotenv>=1.0  # .env 사용 시 선택
```

설치:

```bash
pip install -r requirements.txt
```

---

## 4) 환경 변수 설정

다음 값을 환경 변수로 지정합니다. `.env` 파일을 사용하면 편리합니다.

```dotenv
# .env
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3307       # 기본값 3307
MYSQL_USER=root
MYSQL_PASSWORD=1234
MYSQL_DATABASE=demo_db
```

> 코드 기본값도 위와 동일합니다. 다른 값을 쓰면 `.env` 또는 셸 환경변수로 덮어쓰세요.

---

## 5) MySQL 준비

1. **MySQL 서버 실행**

* 로컬 또는 Docker로 MySQL 8.x를 실행하세요. (포트 `3307` 매핑)
* 예: 호스트의 `3307` → 컨테이너 `3306`

2. **DB 및 권한**

* `demo_db` 데이터베이스가 존재해야 합니다.
* `root/1234` 계정이 접근 가능해야 합니다. (보안상 실제 운영 시 별도의 계정 권장)

3. **테이블 생성**

코드에 포함된 DDL:

```sql
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    age INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

> 현재 제공된 `main.py`는 `startup`에서 `SELECT 1`만 실행합니다.
> 따라서 **최초 1회 위 DDL을 직접 실행**하거나, 아래처럼 `startup`에서 테이블 생성 쿼리도 실행하도록 추가하세요.

```python
# app/main.py 의 on_startup() 예시
@app.on_event("startup")
def on_startup():
    mysql_sync.connect()
    # 테이블 자동 생성
    mysql_sync.execute(SQL.CREATE_TABLE_USERS)
    mysql_sync.execute("SELECT 1")
```

---

## 6) 애플리케이션 실행

스크린샷과 동일하게 **Uvicorn**으로 실행합니다.

```bash
uvicorn app.main:app --reload
```

* 콘솔에 예시와 유사하게 아래가 보이면 정상입니다.

  * `Uvicorn running on http://127.0.0.1:8000`
  * `GET / HTTP/1.1" 200 OK`
  * `GET /favicon.ico HTTP/1.1" 404 Not Found` → **정상** (파비콘 제공하지 않으면 404가 뜹니다.)

---

## 7) API 사용 예시

### (1) 헬스체크

```bash
curl -i http://127.0.0.1:8000/
```

응답 예:

```json
{"message":"OK: FastAPI + MySQL (sync, 3307)"}
```

### (2) 사용자 목록 조회

```bash
curl -i http://127.0.0.1:8000/users
```

### (3) 사용자 생성

```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "age": 29}'
```

### (4) 사용자 단건 조회

```bash
curl -i http://127.0.0.1:8000/users/1
```

### (5) 사용자 수정

```bash
curl -i -X PUT http://127.0.0.1:8000/users/1 \
  -H "Content-Type: application/json" \
  -d '{"username": "alice2", "age": 30}'
```

### (6) 사용자 삭제

```bash
curl -i -X DELETE http://127.0.0.1:8000/users/1
```

---

## 8) 핵심 코드 요약

### 8.1 DB 연결 (동기, PyMySQL) — `app/db.py`

```python
import os
import pymysql
from typing import Optional

class MySQLSync:
    def __init__(self):
        self.conn: Optional[pymysql.connections.Connection] = None

    def connect(self):
        if self.conn:
            return
        host = os.getenv("MYSQL_HOST", "127.0.0.1")
        port = int(os.getenv("MYSQL_PORT", "3307"))
        user = os.getenv("MYSQL_USER", "root")
        password = os.getenv("MYSQL_PASSWORD", "1234")
        db = os.getenv("MYSQL_DATABASE", "demo_db")

        self.conn = pymysql.connect(
            host=host, port=port, user=user, password=password, database=db,
            autocommit=True, charset="utf8mb4",
            cursorclass=pymysql.cursors.Cursor,
        )

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute(self, sql: str, params: tuple = ()):
        assert self.conn is not None, "DB not connected. Call connect() first."
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

mysql_sync = MySQLSync()
```

### 8.2 SQL 상수 — `app/sql.py`

```python
CREATE_TABLE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    age INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

INSERT_USER = "INSERT INTO users (username, age) VALUES (%s, %s)"
SELECT_USERS = "SELECT id, username, age, created_at FROM users ORDER BY id DESC"
SELECT_USER_BY_ID = "SELECT id, username, age, created_at FROM users WHERE id=%s"
UPDATE_USER_BY_ID = "UPDATE users SET username=%s, age=%s WHERE id=%s"
DELETE_USER_BY_ID = "DELETE FROM users WHERE id=%s"
```

### 8.3 FastAPI 엔드포인트 — `app/main.py`

```python
from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Any
from app.db import mysql_sync
import app.sql as SQL

app = FastAPI(title="FastAPI + MySQL (Sync, PyMySQL) - Port 3307")

@app.on_event("startup")
def on_startup():
    mysql_sync.connect()
    # 초기 테이블 생성(권장)
    mysql_sync.execute(SQL.CREATE_TABLE_USERS)
    mysql_sync.execute("SELECT 1")

@app.on_event("shutdown")
def on_shutdown():
    mysql_sync.close()

@app.get("/")
def root():
    return {"message": "OK: FastAPI + MySQL (sync, 3307)"}

@app.get("/users")
def list_users():
    cur = mysql_sync.execute(SQL.SELECT_USERS)
    rows = cur.fetchall()
    result = []
    for r in rows:
        result.append({
            "id": r[0], "username": r[1], "age": r[2],
            "created_at": r[3].isoformat() if r[3] else None
        })
    return result

@app.get("/users/{user_id}")
def get_user(user_id: int):
    cur = mysql_sync.execute(SQL.SELECT_USER_BY_ID, (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "User not found")
    return {
        "id": row[0], "username": row[1], "age": row[2],
        "created_at": row[3].isoformat() if row[3] else None
    }

@app.post("/users", status_code=201)
def create_user(payload: Dict[str, Any] = Body(...)):
    try:
        username = str(payload.get("username", "")).strip()
        age = int(payload.get("age"))
    except Exception:
        raise HTTPException(400, "Invalid body: require username(str) and age(int)")
    if not username:
        raise HTTPException(400, "username required")

    cur = mysql_sync.execute(SQL.INSERT_USER, (username, age))
    user_id = cur.lastrowid

    cur = mysql_sync.execute(SQL.SELECT_USER_BY_ID, (user_id,))
    row = cur.fetchone()
    return {
        "id": row[0], "username": row[1], "age": row[2],
        "created_at": row[3].isoformat() if row[3] else None
    }

@app.put("/users/{user_id}")
def update_user(user_id: int, payload: Dict[str, Any] = Body(...)):
    try:
        username = str(payload.get("username", "")).strip()
        age = int(payload.get("age"))
    except Exception:
        raise HTTPException(400, "Invalid body: require username(str) and age(int)")
    if not username:
        raise HTTPException(400, "username required")

    mysql_sync.execute(SQL.UPDATE_USER_BY_ID, (username, age, user_id))
    cur = mysql_sync.execute(SQL.SELECT_USER_BY_ID, (user_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(404, "User not found")
    return {
        "id": row[0], "username": row[1], "age": row[2],
        "created_at": row[3].isoformat() if row[3] else None
    }

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    mysql_sync.execute(SQL.DELETE_USER_BY_ID, (user_id,))
    return {"message": f"deleted {user_id}"}
```

---

## 9) 트러블슈팅

* **`favicon.ico 404 Not Found`**

  * 정상 현상입니다. 파비콘을 제공하지 않았기 때문입니다.
* **`DB not connected. Call connect() first.`**

  * `MYSQL_*` 환경변수, 포트 매핑, DB 접속 정보 확인.
  * MySQL 가동 여부 확인 (`mysql -h 127.0.0.1 -P 3307 -u root -p`).
* **`username` 중복 에러**

  * `username` 컬럼은 `UNIQUE`. 동일 이름 생성 시 DB에서 오류가 납니다.
* **테이블 미생성으로 인한 오류**

  * 최초 1회 **DDL 실행** 또는 `startup`에서 `CREATE TABLE`을 실행하도록 설정하세요.

---

## 10) 실행 순서 요약

1. 가상환경 구성 및 패키지 설치
2. `.env`(또는 환경변수)로 DB 접속 정보 설정
3. MySQL 실행(포트 3307), `demo_db` 준비
4. `users` 테이블 생성(DDL 실행) **또는** `startup`에 자동 생성 코드 추가
5. 애플리케이션 실행:

   ```bash
   uvicorn app.main:app --reload
   ```
6. 엔드포인트 테스트(`/`, `/users`, `/users/{id}` 등)

---

## 11) 엔드포인트 요약 표

| 메서드    | 경로                 | 설명        | 요청 바디 예시                         | 주요 응답/비고                        |
| ------ | ------------------ | --------- | -------------------------------- | ------------------------------- |
| GET    | `/`                | 헬스체크      | -                                | `{"message":"OK: ... 3307"}`    |
| GET    | `/users`           | 사용자 목록 조회 | -                                | `[{"id":..,"username":..},...]` |
| POST   | `/users`           | 사용자 생성    | `{"username":"alice","age":29}`  | 생성된 사용자 JSON                    |
| GET    | `/users/{user_id}` | 사용자 단건 조회 | -                                | 사용자 JSON / 404                  |
| PUT    | `/users/{user_id}` | 사용자 수정    | `{"username":"alice2","age":30}` | 수정된 사용자 JSON / 404              |
| DELETE | `/users/{user_id}` | 사용자 삭제    | -                                | `{"message":"deleted {id}"}`    |

---

