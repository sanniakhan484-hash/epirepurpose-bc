.PHONY: install data test lint app
install:
	pip install -e ".[dev,app]"
data:
	epirepurpose download
test:
	pytest -q
lint:
	ruff check .
app:
	streamlit run app/streamlit_app.py
