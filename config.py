# This contains the configuration variables for the application
# It is imported by main.py and viewer/application.py
# The Configuration class imports the config.ini file and stores the values in
# the instance variables, it also has a method to update the config.ini file
# with the current values of the instance variables.

import configparser
import os

class Configuration(configparser.ConfigParser):
    """Class to store the configuration variables."""

    def __init__(self, config_file="config.ini"):
        super().__init__()
        self.config_file = config_file
        self.read(config_file)

    def update_config(self):
        """Update the config.ini file with the current values of the instance variables."""
        for section in self.sections():
            for option in self.options(section):
                self.set(section, option, getattr(self, option))
    
    def save_config(self):
        """Save the current configuration to the config.ini file."""
        with open(self.config_file, "w") as configfile:
            self.write(configfile)
    
    def reset_config(self):
        """Reset the configuration to the default values."""
        self.read(self.config_file)
        self.update_config()
    
    def get_config(self):
        """Return the configuration as a dictionary."""
        config = {}
        for section in self.sections():
            config[section] = {}
            for option in self.options(section):
                config[section][option] = self.get(section, option)
        return config

    def get_config_file(self):
        """Return the path to the config.ini file."""
        return self.config_file
    
    def get_config_file_dir(self):
        """Return the directory of the config.ini file."""
        return os.path.dirname(self.config_file)
    
config = Configuration(config_file="config.ini")