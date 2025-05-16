import os
import time

def clean_old_files(directory, days=7):
    now = time.time()
    cutoff = now - (days * 86400)

    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.isfile(filepath):
            if os.path.getmtime(filepath) < cutoff:
                os.remove(filepath)
