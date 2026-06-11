.PHONY: install load dashboard

install:
	pip install -r requirements.txt

load:
	python load_data.py

dashboard:
	streamlit run dashboard/app.py
