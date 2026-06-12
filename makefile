.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	python run_pipeline.py

dashboard:
	streamlit run dashboard/app.py
