import time
import os
import schedule
import getpass
from dotenv import load_dotenv
from capturer import capture_screenshot
from uploader import upload_file

# Load configuration
load_dotenv()

REMOTE_HOST = os.getenv("REMOTE_HOST")
REMOTE_PORT = int(os.getenv("REMOTE_PORT", 22))
REMOTE_USER = os.getenv("REMOTE_USER")
REMOTE_PASSWORD = os.getenv("REMOTE_PASSWORD")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH")

# Dynamic remote directory: /tmp/ScreenShort/<local_username>
LOCAL_USERNAME = getpass.getuser()
REMOTE_BASE_DIR = os.getenv("REMOTE_BASE_DIR", "/tmp/ScreenShort")
REMOTE_DIR = f"{REMOTE_BASE_DIR}/{LOCAL_USERNAME}".replace("//", "/")

INTERVAL = int(os.getenv("INTERVAL_MINUTES", 5))
LOCAL_TEMP = os.getenv("LOCAL_TEMP_DIR", "temp")

def job():
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting task for user: {LOCAL_USERNAME}")
    
    # 1. Capture
    try:
        local_file = capture_screenshot(LOCAL_TEMP)
        print(f"Captured: {local_file}")
    except Exception as e:
        print(f"Error during capture: {e}")
        return

    # 2. Upload
    success = upload_file(
        local_file, 
        REMOTE_DIR, 
        REMOTE_HOST, 
        REMOTE_PORT, 
        REMOTE_USER, 
        key_path=SSH_KEY_PATH, 
        password=REMOTE_PASSWORD
    )

    # success = upload_file(
    #     local_file, 
    #     REMOTE_DIR, 
    #     REMOTE_HOST, 
    #     REMOTE_PORT, 
    #     REMOTE_USER, 
    #     key_path="C:/Users/deepak.p/.ssh/id_ed25519",   ## None
    #     password=None
    # )
    
    # 3. Cleanup local file on success
    if success:
        print("Upload successful. Cleaning up local file...")
        try:
            os.remove(local_file)
        except Exception as e:
            print(f"Error during cleanup: {e}")
    else:
        print("Upload failed. Local file kept for retry or manual check.")

def main():
    print(f"ScreenShort starting. Capturing every {INTERVAL} minutes.")
    print(f"Remote Destination: {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_DIR}")
    
    # Run once immediately
    job()
    
    # Schedule subsequent runs
    schedule.every(INTERVAL).minutes.do(job)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    # Ensure local temp dir exists
    if not os.path.exists(LOCAL_TEMP):
        os.makedirs(LOCAL_TEMP)
    
    main()
