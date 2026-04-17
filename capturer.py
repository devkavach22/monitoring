from PIL import Image
import mss
import mss.tools
from datetime import datetime
import os

def capture_screenshot(output_dir="temp"):
    """
    Captures a screenshot of all monitors and saves it to output_dir with a timestamp.
    Optimized: Saves as JPEG with compression to reduce file size.
    Returns the path to the saved file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.jpg"
    filepath = os.path.join(output_dir, filename)
    
    with mss.mss() as sct:
        # Get the primary monitor
        monitor = sct.monitors[1]
        sct_img = sct.grab(monitor)
        
        # Convert to PIL Image for optimization
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        
        # Save as optimized JPEG
        img.save(filepath, "JPEG", quality=70, optimize=True)
        
    return filepath

if __name__ == "__main__":
    path = capture_screenshot()
    print(f"Screenshot saved to {path}")
