import logging
import sys
import os 
import queue
from concurrent.futures import ThreadPoolExecutor

from viewer.application import MainWindow
from controller.application import MainController  
from worker.watcher import FileWatcher
from config import config
from pathlib import Path

class QueueHandler(logging.Handler):
    """Log handler that outputs to a queue."""

    def __init__(self):
        
        super().__init__()
        self.log_queue = queue.Queue()

    def emit(self, record):
        self.log_queue.put((self.format(record), record.levelname))

class App():
    """Main application class to run the program"""

    def __init__(self, watch_directory) -> None:

        # Initialize logger
        self.log_handler = QueueHandler()
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S", handlers=[self.log_handler]
        )
        
        # Initialize thread manager
        self.worker = ThreadPoolExecutor(max_workers=1)
        
        # Initialize main controller
        self.controller = MainController(
            self.worker, shutdown_cleanup=self.cleanup, log_queue=self.log_handler.log_queue
        )
        
        # Initialize GUI
        self.gui = MainWindow(controller=self.controller, app=self)

        # Set up the GUI
        self.controller.set_view(self.gui)
    
        # Initialize file watcher
        self.file_watcher = FileWatcher(
            watch_directory, process_shot=self.controller.shot_controller.process_shot
        )

    def start(self):
        """Run file watcher and start interface."""
        self.file_watcher.start()
        
        self.gui.master.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.gui.mainloop()

    def cleanup(self):
        """Clean up threads and file watcher. It will pass to
        self.controller and will be implemented when self.controller.quit()
        is called."""
        self.worker.shutdown(wait=False)
        self.file_watcher.stop()
        self.file_watcher.join(3)

    def on_closing(self):
        """Callback for when the GUI is closed."""
        self.controller.quit()

    def update_watch_directory(self, new_directory):
        """Update the watch directory and restart the file watcher."""
        self.file_watcher.stop()
        self.file_watcher = FileWatcher(
            new_directory, process_shot=self.controller.shot_controller.process_shot
        )
        self.file_watcher.start()

if __name__ == "__main__":
    # Get watch directory from command line
    if len(sys.argv) == 2:
        watch_directory = sys.argv[1]
    else:
        watch_directory = os.getcwd()
    
    # Initialize application
    app = App(watch_directory)

    # Run application
    app.start()