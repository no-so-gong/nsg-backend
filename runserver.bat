@echo off
call venv\Scripts\activate
uvicorn app.main:app --host 0.0.0.0 --reload
