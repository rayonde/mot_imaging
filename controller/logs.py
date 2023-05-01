class LogController:
    """
    This class processes the log queue and displays the messages in the GUI.
    """
    def __init__(self, view, log_queue, max_lines=1000, poll_interval=100):
        """
        Initializes a new instance of LogController.

        :param view: The GUI widget instance.
        :type view: View
        :param log_queue: The queue that holds the log messages.
        :type log_queue: multiprocessing.Queue
        :param max_lines: The maximum number of lines to display in the GUI, defaults to 1000.
        :type max_lines: int, optional
        :param poll_interval: The interval at which to poll the log queue in milliseconds, defaults to 100.
        :type poll_interval: int, optional
        """
        self.view = view
        self.log_queue = log_queue
        self.max_lines = max_lines
        self.poll_interval = poll_interval

        self.start_polling()

    def start_polling(self):
        """Starts polling the log queue."""
        self.view.after(self.poll_interval, self.process_log_queue)

    def process_log_queue(self):
        """Processes all new messages in the log queue and displays them in the GUI."""
        while not self.log_queue.empty():
            record = self.log_queue.get(block=False)
            self.view.display(*record)
            self.view.trim_log(self.max_lines)
        self.start_polling()
