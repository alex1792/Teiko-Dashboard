.PHONY: install load dashboard analysis

install:
	pip install -r requirements.txt

load:
	python load_data.py

dashboard:
	streamlit run dashboard/app.py

analysis:
	PYTHONPATH=. python src/analysis/stats_analysis.py
