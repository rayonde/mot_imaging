import signal
import queue

from models.shots import Shot

# import sub controllers
from .logs import LogController
from .shots import ShotController
from .sequences import SequenceController

class MainController:
    def __init__(self, worker, shutdown_cleanup, log_queue):
        self.worker = worker
        self.event_queue = queue.Queue()
        self.log_queue = log_queue
        self.shutdown_cleanup = shutdown_cleanup

        self.view = None
        self.log_controller = None
        self.shot_controller = None
        self.sequence_controller = None

    def set_view(self, view):
        self.view = view
        self.log_controller= LogController(self.view.log, log_queue=self.log_queue)
        self.shot_controller = ShotController(
            self,
            self.worker,
            plot_view=self.view.plot,
            fit_view=self.view.tab.shot_fit,
            list_view=self.view.shot_info_table,
            threeroi_view=self.view.tab.three_roi_atom_count,
            settings_view=self.view.tab.settings
        )
        self.sequence_controller = SequenceController(
            self, self.worker, plot_view=self.view.plot, fit_view=self.view.tab.tof_fit
        )

        # Handle window closure or SIGINT from console
        self.view.master.protocol("WM_DELETE_WINDOW", self.quit)
        signal.signal(signal.SIGINT, self.quit)

        # Start polling event queue
        self.view.after(100, self._poll_event_queue)

    def quit(self, *args, **kwargs):
        """Run callback, then shut down Tkinter master."""
        self.shutdown_cleanup()
        self.view.master.destroy()
        self.view.master.quit()

    def queue(self, func, *args, **kwargs):
        """Add object to event queue (only way to communicate between threads)."""
        return self.event_queue.put((func, args, kwargs))

    def _poll_event_queue(self):
        """The plot queue is polled every 100ms for updates."""
        if not self.event_queue.empty():
            obj = self.event_queue.get(block=False)
            if isinstance(obj, tuple):
                func, *args = obj
                func(*args)
        self.view.after(100, self._poll_event_queue)

    # def _poll_event_queue(self):
    #     """The plot queue is polled every 100ms for updates."""
    #     if not self.event_queue.empty():
    #         obj = self.event_queue.get(block=False)
    #         if isinstance(obj, tuple):
    #             if len(obj) == 1:
    #                 obj[0]()
    #             elif len(obj) == 2:
    #                 if isinstance(obj[1], list):
    #                     obj[0](*obj[1])
    #                 elif isinstance(obj[1], dict):
    #                     obj[0](**obj[1])
    #             elif len(obj) == 3:
    #                 obj[0](*obj[1], **obj[2])
    #     self.view.after(100, self._poll_event_queue)
