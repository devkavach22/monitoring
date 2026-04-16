import mss
import mss.tools
from datetime import datetime
import os

def capture_screenshot(output_dir="temp"):
    """
    Captures a screenshot of all monitors and saves it to output_dir with a timestamp.
    Returns the path to the saved file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"screenshot_{timestamp}.png"
    filepath = os.path.join(output_dir, filename)
    
    with mss.mss() as sct:
        # Get the first monitor (monitor 0 is all monitors)
        # Using monitor 1 for primary or 0 for all monitors combined. 
        # Defaulting to 1 for a single clear screenshot.
        monitor = sct.monitors[1] 
        sct_img = sct.shot(mon=1, output=filepath)
        
    return filepath

if __name__ == "__main__":
    path = capture_screenshot()
    print(f"Screenshot saved to {path}")
