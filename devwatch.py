import sys
import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, target_file):
        self.target_file = target_file
        self.last_reload = 0

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Avoid infinite loops watching the target file itself
        if os.path.abspath(event.src_path) == os.path.abspath(self.target_file):
            return

        # Watch only specific asset directories and file extensions
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext in ['.css', '.js', '.html', '.svg', '.json']:
            now = time.time()
            if now - self.last_reload > 0.5:  # Rate limit reload trigger
                print(f"[DevWatch] File modified: {event.src_path}")
                print(f"[DevWatch] Touching {self.target_file} to trigger Streamlit refresh...")
                try:
                    os.utime(self.target_file, None)
                    self.last_reload = now
                except Exception as e:
                    print(f"[DevWatch] Error touching {self.target_file}: {e}")

if __name__ == "__main__":
    path = "."
    target = "app.py"
    
    # Ensure target exists
    if not os.path.exists(target):
        with open(target, "w") as f:
            f.write("# Skeleton app.py\n")

    event_handler = ReloadHandler(target)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"[DevWatch] Watching folder '{os.path.abspath(path)}' for CSS/JS/HTML changes...")
    print(f"[DevWatch] Changes will touch '{os.path.abspath(target)}'. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
