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

        # Get camera
        self.cam = self.cam_list.GetByIndex(0)

        # Get nodemap
        self.nodemap = self.cam.GetNodeMap()
        self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()

    
    def close(self):
        self.cam_list.Clear()
        self.iface_list.Clear()
        self.system.ReleaseInstance()
        logging.info('Camera controller closed.')

    def device_info(self):
        """Print device info."""
        
        node_device_information = ps.CCategoryPtr(self.nodemap_tldevice.GetNode('DeviceInformation'))
        if ps.IsAvailable(node_device_information) and ps.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = ps.CValuePtr(feature)
                logging.info('%s: %s' % (node_feature.GetName(),
                                        node_feature.ToString() if ps.IsReadable(node_feature) else 'Node not readable'))
        else:
            logging.info('Device control information not available.')
    
    def set_config(self, nodename, value):
        """Set config node."""
        try: 
            node = ps.CIntegerPtr(self.nodemap.GetNode(nodename))
            node_feature = ps.CValuePtr(node)
            if ps.IsWritable(node_feature):
                node_feature.SetValue(value)
                logging.info('%s set to %s' % (node_feature.GetName(), node_feature.ToString()))
            else:
                logging.info('Unable to set %s to %s' % (node_feature.GetName(), node_feature.ToString()))
        except:
            logging.info('Unable to set %s to %s' % (nodename, value))


    def get_config(self, nodename):
        """Get config node."""
        try:
            node = ps.CIntegerPtr(self.nodemap.GetNode(nodename))
            node_feature = ps.CValuePtr(node)

            if ps.IsReadable(node_feature):
                logging.info('%s: %s' % (node_feature.GetName(), node_feature.ToString()))
            else:
                logging.info('Unable to get %s' % node_feature.GetName())
        except:
            logging.info('Unable to get %s' % nodename)


if __name__ == '__main__':
    cam_controller = CameraController()
    n = cam_controller.nodemap.GetNode('AcquisitionFrameRateEnable')
    node = ps.CEnumerationPtr(n)

    print(node.ToString())
    print(node.GetEntryByName('On').GetValue())
    print(node.GetEntryByName('Off').GetValue())
    print(n)
    print(node)
    print(type(n))
    print(type(node))
    cam_controller.close()

    