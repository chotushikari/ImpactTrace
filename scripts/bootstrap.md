# Local bootstrap

## Web

```bash
cd apps/web
npm install
npm run dev
```

## Worker

```bash
cd services/worker
python -m venv .venv
# activate the venv for your shell
pip install -e .
python -m uvicorn app.main:app --reload --port 8001
```

Follow the parent pack's sprints after both health endpoints are working.
