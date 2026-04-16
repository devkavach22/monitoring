import paramiko
from scp import SCPClient
import os
from dotenv import load_dotenv

# Note: scp is usually a separate package but often used with paramiko.
# However, to keep it simple and strictly paramiko as per blueprint, 
# we can use SFTP or a simple SCP implementation via paramiko.
# Let's use SFTP as it's built into Paramiko and very reliable.

def mkdir_p(sftp, remote_directory):
    """
    Recursively creates a remote directory if it doesn't exist.
    """
    if remote_directory == "/":
        sftp.chdir("/")
        return
    if remote_directory == "":
        return
    try:
        sftp.chdir(remote_directory) # Test if it exists
    except IOError:
        dirname, basename = os.path.split(remote_directory.rstrip("/"))
        mkdir_p(sftp, dirname)
        sftp.mkdir(basename)
        sftp.chdir(basename)

def upload_file(local_path, remote_dir, host, port, username, key_path=None, password=None):
    """
    Uploads a file to a remote Linux server using SFTP, creating remote_dir if needed.
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        if key_path:
            ssh.connect(host, port=port, username=username, key_filename=key_path)
        else:
            ssh.connect(host, port=port, username=username, password=password)

        sftp = ssh.open_sftp()

        # Ensure remote directory exists dynamically
        mkdir_p(sftp, remote_dir)

        remote_path = os.path.join(remote_dir, os.path.basename(local_path)).replace("\\", "/")

        print(f"Uploading {local_path} to {remote_path}...")
        sftp.put(local_path, remote_path)
        sftp.close()

        return True
    except Exception as e:
        print(f"Upload failed: {e}")
        return False
    finally:
        ssh.close()


if __name__ == "__main__":
    # For testing purposes only
    load_dotenv()
    # Mock call
    upload_file("C:/Users/deepak.p/Desktop/screenShort/temp/screenshot_20260416_001955.png", "/tmp/ScreenShort", "192.168.11.53", 22, "devtest", key_path=None, password="Shiv.@#kav01")
    pass
