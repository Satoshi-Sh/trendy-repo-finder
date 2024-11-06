#!/bin/bash
cd ~/projects/trendy-repo-finder
source venv/bin/activate
python scraper/scrape.py

current_datetime=$(date '+%Y-%m-%d')
#upload dataset to the kaggle
kaggle datasets version --dir-mode zip -p data -m "Dataset updated on ${current_datetime}"