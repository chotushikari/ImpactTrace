.PHONY: dev test check

dev:
	@echo "Run web: npm --prefix apps/web run dev"
	@echo "Run worker: cd services/worker && python -m uvicorn app.main:app --reload --port 8001"

test:
	cd services/worker && python -m pytest

check:
	npm --prefix apps/web run build
	cd services/worker && python -m pytest
