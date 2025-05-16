import schedule
import time
from scripts.file_cleaner import clean_old_files

def maintenance_tasks():
    clean_old_files("data/videos")
    clean_old_files("data/audio")

def run_maintenance():
    schedule.every().day.at("03:00").do(maintenance_tasks)
    while True:
        schedule.run_pending()
        time.sleep(1)
