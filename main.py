import time
import os
import schedule
import getpass
import uuid
from datetime import datetime
from dotenv import load_dotenv
from capturer import capture_screenshot
from uploader import upload_file

# Load configuration
load_dotenv()

def get_env_or_exit(var_name, default=None, required=True):
    val = os.getenv(var_name, default)
    if required and val is None:
        print(f"CRITICAL ERROR: Environment variable '{var_name}' is not set in .env")
        print("Please configure your .env file before running.")
        exit(1)
    return val

def get_mac_address():
    """Returns the MAC address in XX-XX-XX-XX-XX-XX format."""
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0, 8*6, 8)][::-1])
    return mac.replace(":", "-")

REMOTE_HOST = get_env_or_exit("REMOTE_HOST")
REMOTE_PORT_STR = get_env_or_exit("REMOTE_PORT", "22")
REMOTE_PORT = int(REMOTE_PORT_STR) if REMOTE_PORT_STR else 22
REMOTE_USER = get_env_or_exit("REMOTE_USER")
REMOTE_PASSWORD = get_env_or_exit("REMOTE_PASSWORD", required=False)
SSH_KEY_PATH = get_env_or_exit("SSH_KEY_PATH", required=False)

# Static part of the directory
LOCAL_USERNAME = getpass.getuser()
MAC_ADDRESS = get_mac_address()
REMOTE_BASE_DIR = get_env_or_exit("REMOTE_BASE_DIR", "/tmp/ScreenShort")
USER_DIR_NAME = f"{LOCAL_USERNAME}_{MAC_ADDRESS}"

INTERVAL_STR = get_env_or_exit("INTERVAL_MINUTES", "5")
INTERVAL = int(INTERVAL_STR) if INTERVAL_STR else 5
LOCAL_TEMP = get_env_or_exit("LOCAL_TEMP_DIR", "temp")

def get_remote_path():
    """Generates the dynamic remote path: base/user_mac/today_date"""
    today_date = datetime.now().strftime("%d_%m_%Y")
    path = f"{REMOTE_BASE_DIR}/{USER_DIR_NAME}/{today_date}".replace("//", "/")
    return path

def job():
    if not REMOTE_HOST or not REMOTE_USER:
        print("Missing required configuration (REMOTE_HOST or REMOTE_USER). Skipping task.")
        return

    current_remote_dir = get_remote_path()
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] Starting task for user: {LOCAL_USERNAME}")
    print(f"Destination: {current_remote_dir}")

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
        current_remote_dir, 
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
    print(f"Remote Destination: {REMOTE_USER}@{REMOTE_HOST}:{get_remote_path()}")
    
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
