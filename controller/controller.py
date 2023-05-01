import signal
import queue
from .log import LogController
from .shot import ShotController
from .sequence import SequenceController

class MainController:
    """This class handles the data and queues"""
    def __init__(self, worker, *, shutdown_cleanup, log_queue):
        self.worker = worker
        self.event_queue = queue.Queue()
        self.log_queue = log_queue
        self.shutdown_cleanup = shutdown_cleanup

        # Initialize other controllers
        self.view, self.log_controller, self.shot_controller, self.sequence_controller = None, None, None, None

    def set_controller(self, view):
        # view is the main gui instance from MainWindow
        self.view = view
        
        
        # Handle window closure or SIGINT from console
        self.view.master.protocol("WM_DELETE_WINDOW", self.quit)
        signal.signal(signal.SIGINT, self.quit)

    
    
    def _initialize_presenters(self):
        self.log_presenter = LogController(self.view.logs, log_queue=self.log_queue)
        self.shot_presenter = ShotController()
        self.sequence_presenter = SequenceController()