source ./app/.venv/bin/activate
pip install -r app/requirements.txt
cd app
AWS_PROFILE=patrick-personal python3 -m uvicorn main:app --env-file .env --reload
