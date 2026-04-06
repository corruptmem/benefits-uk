.PHONY: help compute test clean serve deploy

help:
	@echo "UK Benefits Calculator — Make targets"
	@echo "  make compute     — run precomputation"
	@echo "  make serve      — serve www/ locally"
	@echo "  make test       — run basic smoke tests"
	@echo "  make clean      — remove generated data"

compute:
	python -m compute.compute --gzip

serve:
	python -m http.server 8080 --directory www

test:
	@python -c "from compute import benefits, tax; print('Python modules OK')"

clean:
	rm -rf data/output
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
