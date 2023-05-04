import PySpin as ps
import numpy as np
import time 
import logging
from platform import node 
import os 

class CameraController:
    def __init__(self, main_controller, worker, camera_view) -> None:
        self.main_controller = main_controller
        self.worker = worker
        self.camera_view = camera_view

        self.system = ps.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        logging.info('Library version: %d.%d.%d.%d' % (self.version.major, self.version.minor, self.version.type, self.version.build))
    
        # Interface list 
        self.iface_list = self.system.GetInterfaces()
        self.num_interfaces = self.iface_list.GetSize()
        logging.info('Number of interfaces detected: %i' % self.num_interfaces)
    
        # Camera list 
        self.cam_list = self.system.GetCameras()
        self.num_cams = self.cam_list.GetSize()
        logging.info('Number of cameras detected: %i' % self.num_cams)
        