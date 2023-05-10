import yaml
from pathlib import Path
import numpy as np
import os 

class Configuration(dict):
    """Class to store the configuration variables."""

    def __init__(self, config_file="config.yaml"):
        super().__init__()  # initialize as a dictionary
        self.config_file = Path(config_file)
        self.reload_config()

        self.fit = True
        self.fit_2D = True
        self.roi_enabled = False
        self.three_roi_enabled = False
        self.fix_center = False
 

    def save(self):
        """Save the current configuration to the config file."""
        with open(self.config_file, "w") as f:
            yaml.dump(dict(self), f)
    
    def get_config(self, section, key):
        """Return the configuration as a dictionary."""
        if section in self.keys():
            if key in self[section].keys():
                return self[section][key]
            else:   
                return None
        else:
            return None

    def reload_config(self, path=None):
        """Reload the configuration from the config file."""
        if path:
            self.config_file = Path(path)
        with open(self.config_file, "r") as f:
            self.clear()
            self.update(yaml.safe_load(f) or {})

    @property
    def camera_name(self):
        return self["camera"]["name"]
    
    @property
    def pixel_size(self):
        var = self["camera_info"]["RealPixelSize"]
        if var:
            return float(var) * 1e-3
        else:
            return None
    
    @property
    def exposure_time(self):
        var = self["camera"]["ExposureTime"]
        if var:
            return float(var)
        else:
            return None
    
    @property
    def trigger_delay(self):
        var = self["camera"]["TriggerDelay"]
        if var:
            return float(var)
        else:
            return None
        
    @property
    def atom_mass(self):
        var = self["atoms"]["mass"]
        if var:
            return float(var)
        else:
            return None
    
    @property
    def repump_time(self):
        var = self["repump"]["repump_time"]
        if var:
            return float(var)
        else:
            return None
    
    @property
    def cooling_time(self):
        var = self["cooling"]["cooling_time"]
        if var:
            return float(var) 
        else:
            return None
    
    @property
    def magnification(self):
        var = self["beam"]["magnification"]
        if var:
            return float(var)
        else:
            return None
        
    @property
    def wavelength(self):
        var = self["beam"]["wavelength"]
        if var:
            return float(var) * 1e-9
        else:
            return None
    
    @property
    def detuning(self):
        var = self["beam"]["detuning"]
        if var:
            return float(var) * 2 * np.pi
        else:
            return None
    
    @property
    def linewidth(self):
        var = self["beam"]["linewidth"]
        if var:
            return float(var) * 2 * np.pi
        else:
            return None
    
    @property
    def physical_scale(self):
        return self.pixel_size * (1/self.magnification)
    
    @property
    def colormap(self):
        return self.get_config("plot", "colormap")
    
    ##### Fit Settings #####
    @property
    def fit_optical_density(self):
        """If True, fits are done against the atom density (-ln(OD))."""
        var = self.get_config("fit", "fit_optical_density")
        if var:
            return bool(var)
        else:
            return False

    @fit_optical_density.setter
    def fit_optical_density(self, val):
        self["fit"]["fit_optical_density"] = str(val)

    @property
    def fix_theta(self):
        """If True, 2D Gaussian fit restricts theta to 0 (hor/ver)."""
        var = self.get_config("fit", "fix_theta")
        if var:
            return bool(var)
        else:
            return False

    @fix_theta.setter
    def fix_theta(self, val):
        self["fit"]["fix_theta"] = str(val)

    @property
    def fix_z0(self):
        """If True, 2D Gaussian fit restricts z0 to 0."""
        var = self.get_config("fit", "fix_z0")
        if var:
            return bool(var)
        else:
            return False

    @fix_z0.setter
    def fix_z0(self, val):
        self["fit"]["fix_z0"] = str(val)

    @property
    def roi(self):
        """Tuple of (x0, y0, x1, y1) defining the region of interest for fitting."""
        var = self.get_config("fit", "roi")
        if var:
            return tuple(var)
        else:   
            return None

    @roi.setter
    def roi(self, tup):
        self["fit"]["roi"] = list(tup)

    @property
    def threeroi(self):
        """Tuple of (x0,y0,x1,y1,x2,y2,x3,y3,x4,y4,x5,y5) defining three regions of interests (0,1), (2,3), (4,5) for atom counting and subsequent subtraction."""
        var = self.get_config("fit", "threeroi")
        if var:
            return tuple(var)
        else:
            return None

    @threeroi.setter
    def threeroi(self,tup):
        self["fit"]["threeroi"] = list(tup)

    @property
    def tof(self):
        """List of time of flight shot times in ms for temperature fitting."""
        var = self.get_config("fit", "tof")
        if var:
            return list(var)
        else:
            return None

    @tof.setter
    def tof(self, arr):
        self["fit"]["tof"] = list(arr)

    @property
    def center(self):
        """Tuple of (x, y) - 2D Gaussian fit restricted to this center point."""
        var = self.get_config("fit", "center")
        if var:
            return tuple(var)
        else:
            return None
        

    @center.setter
    def center(self, tup):
        self["fit"]["center"] = list(tup)
    
    # TODO: check if this is used anywhere
    # @property
    # def logdict(self):
    #     """Returns dictionary of all relevant config parameters"""
    #     return {"fittedshot" : self.fit,
    #             "fittedshot2D" : self.fit_2D,
    #             "roi_enabled" : self.roi_enabled,
    #             "three_roi_enabled" : self.three_roi_enabled,
    #             "magnification(x)" : self.magnification,
    #             "pixel_size(mm)" : self.pixel_size,
    #             "wavelength(nm)" : self.wavelength,
    #             "detuning(MHz)" : self.detuning,
    #             "linewidth(MHz)" : self.linewidth,
    #             "repump_time(ms)" : self.repump_time,
    #             "atom_mass(kg)" : self.atom_mass
    #         }

    def get_config_file(self):
        return os.path(self.config_file)
    
    def get_config_file_dir(self):
        return os.path.dirname(self.config_file)

config = Configuration(config_file="config.yaml")