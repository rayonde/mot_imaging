import logging
from pathlib import Path
from datetime import date
import time
import h5py
from utils.threading import mainthread
from models import sequences
from config import config

class SequenceController: 
    def __init__(self, app, worker, plot_view, fit_view):
        self.app = app
        self.worker = worker
        self.plot_view = plot_view
        self.fit_view = fit_view

        self.current_tof = None
        self.current_atom_opt = None
 
    @mainthread
    def display_tof(self, tof):
        self.plot_view.display(tof)
        self.fit_view.display(tof)

    @mainthread
    def display_atom_opt(self, ao):
        self.plot_view.display(ao)

    def start_tof(self, times):
        self.current_tof = sequences.TimeOfFlight(times)
        logging.info(f"Starting Time of Flight (ms): {times}")

    def start_atom_opt(self, params):
        self.current_atom_opt = sequences.AtomNumberOptimization(params)
        logging.info(f"Starting Atom Number Optimization: {params}")

    def start_tof_selection(self, times):
        selection = self._get_shot_selection(times)
        if selection:
            self.start_tof(times)
            for shot in selection:
                self.current_tof.add(shot, self._handle_sequence_completion)

    def start_atom_opt_selection(self, params):
        selection = self._get_shot_selection(params)
        if selection:
            self.start_atom_opt(params)
            for shot in selection:
                self.current_atom_opt.add(shot, self._handle_sequence_completion)

    def add_shot(self, shot):
        if self.current_tof:
            self.current_tof.add(shot, self._handle_sequence_completion)
        if self.current_atom_opt:
            self.current_atom_opt.add(shot, self._handle_sequence_completion)

    def _handle_sequence_completion(self, sequence):
        if isinstance(sequence, sequences.TimeOfFlight):
            self.app.queue(self.display_tof, sequence)
            with h5py.File(self._output_log_path(), "a") as logfile:
                lf = logfile.create_group(f"/tof_sequence/{time.strftime('%H:%M:%S')}")
                lf.attrs['filename'] = str([shot.name for shot in sequence.shots])
                lf.create_dataset("atom_number", data=sequence.atom_number)
                lf.create_dataset("time_sequence", data=sequence.t)
                lf.attrs['average_T(uK)'] = str(sequence.avg_temp)
                lf.attrs.update(config.logdict)

        elif isinstance(sequence, sequences.AtomNumberOptimization):
            self.app.queue(self.display_atom_opt, sequence)
            with h5py.File(self._output_log_path(), "a") as logfile:
                lf = logfile.create_group(f"/atomnum_sequence/{time.strftime('%H:%M:%S')}")
                lf.attrs['filename'] = str([shot.name for shot in sequence.shots])
                lf.create_dataset("atom_number", data=sequence.atom_number)
                lf.attrs.update(config.logdict)

    def _get_shot_selection(self, params):
        selection = self.app.shot_presenter.shotlist_selection
        if len(selection) != len(params):
            logging.error(
                "Sequence mismatch! %i selected for %i params",
                len(selection),
                len(params),
            )
            return False
        return selection

    def _output_log_path(self):
        """Returns the path to the output log file."""
        output = Path("data/").joinpath(str(date.today()))
        output.mkdir(parents=True, exist_ok=True)
        return output.joinpath("000_logging.hdf5")

