import logging
import sys
import os 
import queue

class QueueHandler(logging.Handler):
    """Log handler that outputs to a queue."""

    def __init__(self):
        super().__init__()
        self.log_queue = queue.Queue()

    def emit(self, record):
        self.log_queue.put((self.format(record), record.levelname))

class App():
    """Main application class to run the program"""

    def __init__(self) -> None:
        # Initialize logger
        self.log_handler = QueueHandler()
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[self.log_handler],
        )
