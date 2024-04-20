import time
import subprocess

while True:
    # Execute your Python script here
    subprocess.run(["python", "botFechasDisponibles.py"])
    # Wait for 5 minutes
    time.sleep(300)
