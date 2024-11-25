#!/bin/bash
echo "Starting script at $(date)" >> /var/log/trendy.log
cd ~/projects/trendy-repo-finder
source venv/bin/activate
python scraper/scrape.py

current_datetime=$(date '+%Y-%m-%d')
echo "Dataset update time: $current_datetime" >> /var/log/trendy.log
kaggle datasets version  -p data -m "Dataset updated on ${current_datetime}"
echo "Script finished at $(date)" >> /var/log/trendy.log
