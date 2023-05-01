import logging
from collections import deque
from threading import Lock
from pathlib import Path
from datetime import date
import time
import h5py
from matplotlib.figure import Figure

from utils.threading import mainthread
from models import shots
from config import config

class ShotPresenter:
    def __init__(self, app, worker, *, plot_view, fit_view, list_view, threeroi_view, settings_view):
        self.app = app
        self.worker = worker
        self.plot_view = plot_view
        self.fit_view = fit_view
        self.list_view = list_view
        self.threeroi_view = threeroi_view
        self.settings_view = settings_view

        # Stores data for past (maxlen) shots
        self.recent_shots = deque(maxlen=15)
        self.current_shot = None
        self.shotlist_selection = ()
        
        self.recent_shots_lock = Lock()
        
    
    def process_shot(self, name, paths):
        logging.info("\n-------------------------------")
        logging.info("1: PROCESSING SHOT %s", name)

        shot = shots.Shot(name, paths)
        self.current_shot = shot
        self._update_recent_shots(shot)

        self.app.queue(self.display_shot, shot)  # Display raw aborption image

        if config.fit:
            shot.run_fit(config)
            self.app.queue(self.display_shot, shot)  # Display fit overlay

        # Save to png output
        figure = Figure(figsize=(8, 5))
        shot.plot(figure)
        figure.savefig(_output_path(name), dpi=150)


        # Saves fit params to log file
        cmnts = self.settings_view.get_comment()
        logging.info("Updating logging.csv for shot %s with comment %s " % (name, cmnts))

        output_log_path = _output_log_path(name)
        with h5py.File(output_log_path, "a") as logfile:
            group_name = str(time.strftime('%H:%M:%S'))
            group = logfile.create_group(group_name)
            group.create_dataset("atom", data=shot.data)
            group.create_dataset("beam", data=shot.beam)
            group.create_dataset("dark", data=shot.dark)
            group.attrs['filename'] = str(name)
            group.attrs['atom_number'] = shot.atom_number

            for label, value in config.logdict.items():
                group.attrs[label] = value

            if config.roi_enabled:
                group.attrs["roi"] = config.roi
                group.attrs['fit_vars'] = shot.fit.best_values

            if config.three_roi_enabled:
                group.attrs['a_b_ratio'] = shot.three_roi_atom_number["a_b_ratio"]
                group.attrs["threeroi"] = config.threeroi

            group.attrs["comments"] = cmnts

        # Check if ToF or optimization
        self.app.sequence_presenter.add_shot(shot)


    def _update_recent_shots(self, shot):
        with self.recent_shots_lock:
            if shot in self.recent_shots:
                idx = self.recent_shots.index(shot)
                self.recent_shots.remove(shot)
                self.recent_shots.insert(idx, shot)
            else:
                self.recent_shots.append(shot)


    @mainthread
    def display_shot(self, shot):
        """Updates the data display with new info."""
        self.plot_view.display(shot)

        self.fit_view.clear()
        if shot.fit:
            self.fit_view.display(dict({"N": shot.atom_number}, **shot.fit.best_values))
        else:
            self.fit_view.display({"N": shot.atom_number})

        with self.recent_shots_lock:
            self.list_view.refresh(self.recent_shots)
            self.list
