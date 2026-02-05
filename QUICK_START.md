# 빠른 시작

## 1. 설치
```bash
pip install -r requirements.txt
```

## 2. Snowflake 설정
`.streamlit/secrets.toml`:
```toml
[connections.snowflake]
account = "your_account"
user = "your_user"
password = "your_password"
role = "ACCOUNTADMIN"
warehouse = "COMPUTE_WH"
database = "your_db"
schema = "PUBLIC"
```

## 3. 실행
```bash
cd problems/Day1
streamlit run app_1_1.py
```

---

**실습 순서**: Day1 → Day2 → Day3
