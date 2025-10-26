# FastAPI + MySQL (Sync, PyMySQL) - Port 3307

전체를 **동기 연결(Python + PyMySQL)** 로 전환한 버전입니다.
- 비동기 `aiomysql` → **동기 `PyMySQL`**
- 엔드포인트 `def` 기반 (블로킹 I/O)
- `lifespan`(동기 컨텍스트)로 시작/종료 관리 (`on_event` 미사용)
- 기본 MySQL 포트 **3307**

## 1) MySQL 3307 설정 & 초기화
MySQL 설정(`my.cnf`) 예시:
```ini
[mysqld]
port=3307
bind-address=0.0.0.0
character-set-server=utf8mb4
collation-server=utf8mb4_0900_ai_ci
```

초기 스크립트 실행(관리자 계정):
```bash
mysql -u root -p -P 3307 -h 127.0.0.1 < scripts/mysql_init.sql
```

## 2) 실행 절차
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# (필요 시) 환경변수 override
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3307
export MYSQL_USER=appuser
export MYSQL_PASSWORD=app_pass_1212
export MYSQL_DATABASE=demo_db

uvicorn app.main:app --reload
```

## 3) 주요 파일
- `app/db.py` : **PyMySQL** 동기 커넥션 (connect/close/execute)
- `app/main.py` : **동기 라우트**, `lifespan`(동기)로 startup/shutdown 처리
- `app/sql.py` : 순수 SQL
- `scripts/mysql_3307_init.sql` : DB/계정/테이블/시드

## 4) 주의사항
- 동기 I/O라서 많은 동시 요청 시 처리량이 낮을 수 있습니다. 필요하면 **Uvicorn/Gunicorn 워커 수**를 늘려 병렬 처리하세요.
  ```bash
  # 예: 4 워커
  uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
  ```
