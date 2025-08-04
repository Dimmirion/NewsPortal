@echo off
call venv\Scripts\activate
celery -A NewsPortal worker --loglevel=info --pool=solo
pause