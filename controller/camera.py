import PySpin as ps
import numpy as np
import time 
import logging
from platform import node 
import os 

class CameraController:
    def __init__(self) -> None:
        # self.main_controller = main_controller
        # self.worker = worker
        # self.camera_view = camera_view

        self.system = ps.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.version = self.system.GetLibraryVersion()
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
        print (self.cam)
        self.cam.Init()
        # Get nodemap
        self.nodemap = self.cam.GetNodeMap()
        self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
    
    def acquisition(self, num_images=10, filename='test', for):
        """Acquire image."""

        MAX_IMAGES = 5000
        num_images = 0

        self.cam.BeginAcquisition()
        logging.info('Camera acquisition starts.')
    
    def close(self):
        self.cam.DeInit()
        del self.cam
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
    
    def config_trigger(self, exposure_time='min', trigger='Line3'):
        """Configure trigger."""
        
        self.set_config('GainAuto', 'Off')

        self.set_config('TriggerMode', 'On')
        self.set_config('TriggerSource', trigger)
        self.set_config('TriggerSelector', 'ExposureStart')
        self.set_config('TriggerActivation', 'RisingEdge')

        self.set_config('ExposureMode', 'Timed')
        self.set_config('ExposureAuto', 'Off')
        self.set_config('ExposureTime', exposure_time)
    
    def config_fomat(self, pixel_format='Mono8'):
        """Configure image format."""

        self.set_config('PixelFormat', pixel_format)
      
    def set_config(self, nodename, value):
        """Set config node."""
        node_address = self.nodemap.GetNode(nodename)
        
        if ps.IsAvailable(node_address) and ps.IsWritable(node_address):
            
            if ps.CEnumEntryPtr(node_address).IsValid():
                node = ps.CEnumerationPtr(node_address)
                node_entry = ps.CEnumEntryPtr(node.GetEntryByName(value))
                entry_value = node_entry.GetValue()
                
                node.SetIntValue(entry_value)
                logging.info('%s set to %s' % (node.GetName(), value))
            
            elif ps.CIntegerPtr(node_address).IsValid():
                node = ps.CIntegerPtr(node_address)

                if isinstance(value, str):
                    if value == 'min':
                        value = node.GetMin()
                    elif value == 'max':
                        value = node.GetMax()
                    else:
                        logging.info('Value %s is not valid.' % value)
                else:
                    value = int(value)

                if node.GetMin() <= value <= node.GetMax():
                    node.SetValue(value)
                    logging.info(f'{node.GetName()} set to {value}')
                else:
                    logging.info('Value %s is out of range.' % value)

            
            elif ps.CFloatPtr(node_address).IsValid():
                node = ps.CFloatPtr(node_address)

                if isinstance(value, str):
                    if value == 'min':
                        value = node.GetMin()
                    elif value == 'max':
                        value = node.GetMax()
                    else:
                        logging.info('Value %s is not valid.' % value)
                else:
                    value = int(value)

                if node.GetMin() <= value <= node.GetMax():
                    node.SetValue(value)
                    logging.info(f'{node.GetName()} set to {value}')
                else:
                    logging.info('Value %s is out of range.' % value)


            elif ps.CBooleanPtr(node_address).IsValid():
                node = ps.CBooleanPtr(node_address)
                
                value = bool(value)
                node.SetValue(value)
                logging.info('%s set to %s' % (node.GetName(), value))

            else:
                logging.info('Type of node is not supported temporarily.')
        else:
            logging.info('Node %s is not available' % nodename)
        
    def get_config(self, nodename):
        """Get config node."""
        node_address = self.nodemap.GetNode(nodename)

        if ps.IsAvailable (node_address) and ps.IsReadable(node_address):

            # Enumeration node
            if ps.CEnumerationPtr(node_address).IsValid():
                node = ps.CEnumerationPtr(node_address)
                node_feature = node.GetCurrentEntry()

                if ps.IsReadable(node_feature):
                    node_feature_symbol = node_feature.GetSymbolic()
                    logging.info('%s: %s' % (node.GetName(), node_feature_symbol))
                    return node_feature_symbol
                else:
                    logging.info('Unable to get %s' % node.GetName())

            # Integer node
            elif ps.CIntegerPtr(node_address).IsValid():
                node = ps.CIntegerPtr(node_address)
                node_feature = node.GetValue()
                
                if ps.IsReadable(node_feature):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('Unable to get %s' % node.GetName())
            
            # Float node
            elif ps.CFloatPtr(node_address).IsValid():
                node = ps.CFloatPtr(node_address)
                node_feature = node.GetValue()

                if ps.IsReadable(node_feature):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('Unable to get %s' % node.GetName())
            
            # Boolean node
            elif ps.CBooleanPtr(node_address).IsValid():
                node = ps.CBooleanPtr(node_address)
                node_feature = node.GetValue()

                if ps.IsReadable(node_feature):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('Unable to get %s' % node.GetName())

            elif ps.CCommandPtr(node_address).IsValid():
                logging.info('Command node is not supported temporarily.')
            elif ps.CStringPtr(node_address).IsValid():
                logging.info('String node is not supported temporarily.')
            elif ps.CRegisterPtr(node_address).IsValid():
                logging.info('Register node is not supported temporarily.')
            elif ps.CCategoryPtr(node_address).IsValid():
                logging.info('Category node is not supported temporarily.') 
        else: 
            logging.info('Unable to get %s' % nodename)


if __name__ == '__main__':
    cam_controller = CameraController()
    n = cam_controller.nodemap.GetNode('AcquisitionMode')
    node = ps.CEnumerationPtr(n)
    print("------------------------------------")
    print("====================================")
    print(n)
    print(node)
    node_feature = node.GetCurrentEntry()
    print(ps.IsReadable(node_feature))
    print(node_feature)

    #print(node_feature_symbol)
    #print(node_feature.ToString())
    # print(node.GetEntries())
 

    cam_controller.close()

