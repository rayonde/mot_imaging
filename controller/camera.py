from typing import Any
import PySpin as ps
import numpy as np
import time 
import logging
from platform import node 
import os 
import threading

def thread(func):
    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        return t
    return wrapper

class CameraController:
    def __init__(self) -> None:
        """
        The initialization of the camera controller turns on the camera 
        retrieve the camera info and settings, and then release the camera.
        """
        self.exposure_time = 50
        self.trigger_source = 'Line0'
        self.trigger_delay = 0.0
        self.pixel_format = 'Mono8'
        self.file_format = 'bmp'
        self.filename = 'test'
        self.folder = 'data'
        self.tag = '1'
        self.device_config = {}
        self.camera_config = {}
        self.isavailable = False

        cam, cam_list, system = self.find_camera()
        if cam is not None:
            self.device_info(cam)
            nodemap, tldevice_nodemap = self.nodemap(cam)
            self.camera_config = self.get_all_config(nodemap)

        self.close(cam, cam_list, system)

    def update_camera_config(self, nodemap):
        """Update camera config."""
        for name in self.camera_config.keys():
            self.camera_config[name] = self.get_config(nodemap, name)

    def retrieve_config(self, name:str) -> Any:
        if name in self.device_config.keys():
            return self.device_config[name]
        elif name in self.camera_config.keys():
            return self.camera_config[name]
        else:
            logging.info('Config name %s is not available.' % name)
            return None

    def find_camera(self):
        logging.info('============= find camera =============')
        system = ps.System.GetInstance()
        cam_list = system.GetCameras()
        version = system.GetLibraryVersion()
        logging.info('Library version: %d.%d.%d.%d' % (version.major, version.minor,version.type, version.build))
        
        num_cameras = cam_list.GetSize()
        logging.info('Number of cameras detected: %i' % num_cameras)
        if num_cameras == 0:
            # Clear camera list before releasing system
            cam_list.Clear()
            # Release system instance
            system.ReleaseInstance()
            logging.info('Not enough cameras!')
            return None, None, None
        else:
            cam = cam_list.GetByIndex(0)
            self.isavailable = True
            logging.info('Camera is found.')
            return cam, cam_list, system
    
    def close(self, cam, cam_list, system):
        if cam is not None:
            cam.DeInit()
            del cam
        if cam_list is not None:
            cam_list.Clear()
        if system is not None:
            system.ReleaseInstance()
        logging.info('Camera is closed.')
    
    def nodemap(self, cam) -> Any:
        """Get nodemap."""
        if cam is not None:
            nodemap = cam.GetNodeMap()
            tldevice_nodemap = cam.GetTLDeviceNodeMap()
            return nodemap, tldevice_nodemap
        else:
            logging.info('Camera is not available.')
            return None, None
        
    def device_info(self, cam) -> bool:
        """Print device info."""

        if cam is not None:
            nodemap = cam.GetNodeMap()
        else:
            logging.info('Camera is not available.')
            return False

        logging.info('============= device info update =============')
        try:
            result = True
            node_device_information = ps.CCategoryPtr(nodemap.GetNode('DeviceInformation'))
            if ps.IsReadable(node_device_information):
                features = node_device_information.GetFeatures()
                for feature in features:
                    node_feature = ps.CValuePtr(feature)
                    logging.info('%s: %s' % (node_feature.GetName(),
                                            node_feature.ToString() if ps.IsReadable(feature) else 'Node not readable'))
                    
                    if ps.IsReadable(feature):
                        self.device_config[node_feature.GetName()] = node_feature.ToString()
            else:
                logging.info('Device control information not available.')
                return False
        except ps.SpinnakerException as ex:
            logging.info('Error: %s' % ex)
            return False
    
    def set_config(self, nodemap, nodename, value) -> bool:
        """Set config node."""
        if nodemap is None:
            logging.info('Camera is not available to set configurations.')
            return False
        
        node_address = nodemap.GetNode(nodename)
        if not ps.IsAvailable(node_address):
            logging.info('Node %s is not available' % nodename)
            return False
        else:
            # check node type
            if ps.CEnumerationPtr(node_address).IsValid():
                node = ps.CEnumerationPtr(node_address)
                node_entry = ps.CEnumEntryPtr(node.GetEntryByName(value))
                try:
                    node.SetIntValue(node_entry.GetValue())
                    logging.info('%s set to %s' % (node.GetName(), value))
                except:
                    logging.info('Value %s is not valid.' % value)
                    return False
            
            elif ps.CIntegerPtr(node_address).IsValid():
                node = ps.CIntegerPtr(node_address)
                try:
                    node.SetValue(int(value))
                    logging.info('%s set to %s' % (node.GetName(), value))
                except:
                    logging.info('Value %s is not valid.' % value)
                    return False
            
            elif ps.CFloatPtr(node_address).IsValid():
                node = ps.CFloatPtr(node_address)
                try:
                    node.SetValue(float(value))
                    logging.info('%s set to %s' % (node.GetName(), value))
                except:
                    logging.info('Value %s is not valid.' % value)
                    return False
            
            elif ps.CBooleanPtr(node_address).IsValid():
                node = ps.CBooleanPtr(node_address)
                try:
                    node.SetValue(bool(value))
                    logging.info('%s set to %s' % (node.GetName(), value))
                except:
                    logging.info('Value %s is not valid.' % value)
                    return False
            
            else:
                logging.info('Type of node is not supported temporarily.')
                return False
            
    def get_config(self, nodemap, nodename) -> Any:
        """Get config node."""
        if nodemap is None:
            logging.info('Camera is not available to get configurations.')
            return None
        
        node_address = nodemap.GetNode(nodename)
        if not ps.IsAvailable(node_address):
            logging.info('Node %s is not available' % nodename)
            return None
        else:
            # check node type
            if ps.CEnumerationPtr(node_address).IsValid():
                node = ps.CEnumerationPtr(node_address)
                node_feature = node.GetCurrentEntry()
                if ps.IsReadable(node):
                    node_feature_symbol = node_feature.GetSymbolic()
                    logging.info('%s: %s' % (node.GetName(), node_feature_symbol))
                    return node_feature_symbol
                else:
                    logging.info('(Enumeration)Unable to get %s' % node.GetName())
                    return None
            
            elif ps.CIntegerPtr(node_address).IsValid():
                node = ps.CIntegerPtr(node_address)
                node_feature = node.GetValue()
                if ps.IsReadable(node):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('(Int)Unable to get %s' % node.GetName())
                    return None
            
            elif ps.CFloatPtr(node_address).IsValid():
                node = ps.CFloatPtr(node_address)
                node_feature = node.GetValue()
                if ps.IsReadable(node):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('(Float)Unable to get %s' % node.GetName())
                    return None
            
            elif ps.CBooleanPtr(node_address).IsValid():
                node = ps.CBooleanPtr(node_address)
                node_feature = node.GetValue()
                if ps.IsReadable(node):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('(Bool)Unable to get %s' % node.GetName())
                    return None
                
            elif ps.CStringPtr(node_address).IsValid():
                node = ps.CStringPtr(node_address)
                node_feature = node.GetValue()
                if ps.IsReadable(node):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('(String)Unable to get %s' % node.GetName())
                    return None 
            else:
                logging.info('Type of node is not supported temporarily.')
                return None

    def get_all_config(self, nodemap) -> dict:
        """Get all config nodes."""
        if nodemap is None:
            logging.info('Camera is not available to get configurations.')
            return None
        
        config = {}
        for nodename in nodemap.GetNodeNames():
            config[nodename] = self.get_config(nodemap, nodename)
        return config
     
    def config_trigger(self, 
                       nodemap, 
                       exposure_time:float=None, 
                       trigger:str=None, 
                       trigger_delay:float=None) -> bool:
        if nodemap is None:
            logging.info('Camera is not available to set configurations.')
            return False
        if exposure_time is not None:
            self.exposure_time = exposure_time
        if trigger is not None:
            self.trigger_source = trigger
        if trigger_delay is not None:
            self.trigger_delay = trigger_delay
        
        logging.info('============= config trigger =============')
        try: 
            self.set_config(nodemap, 'TriggerMode', 'Off')
            self.set_config(nodemap, 'GainAuto', 'Off')
            self.set_config(nodemap, 'TriggerSource', self.trigger_source)
            self.set_config(nodemap, 'TriggerSelector', 'ExposureStart')
            self.set_config(nodemap, 'TriggerActivation', 'RisingEdge')
            self.set_config(nodemap, 'TriggerDelay', self.trigger_delay)
            self.set_config(nodemap, 'ExposureMode', 'Timed')
            self.set_config(nodemap, 'ExposureAuto', 'Off')
            self.set_config(nodemap, 'ExposureTime', self.exposure_time)

            self.set_config(nodemap, 'TriggerMode', 'On')
            self.set_config(nodemap, 'AcquisitionMode', 'Continuous')
                                         
        except ps.SpinnakerException as ex:
            logging.info('Error: %s' % ex)
            return False

    def config_fomat(self, nodemap, pixel_format:str=None) -> bool:
        """Configure image format."""
        if nodemap is None:
            logging.info('Camera is not available to set configurations.')
            return False
        
        if pixel_format is not None:
            self.pixel_format = pixel_format
        
        try:
            self.set_config(nodemap, 'PixelFormat', self.pixel_format)
            return True
        except ps.SpinnakerException as ex:
            logging.info('Error: %s' % ex)
            return False
    
    def reset_cam(self, cam) -> bool:
        """Reset camera to default settings."""
        if cam is None:
            logging.info('Camera is not available to set configurations.')
            return False
        
        logging.info('Resetting camera to default settings...')
        try:
            cam.UserSetSelector.SetValue(ps.UserSetSelector_Default)
            cam.UserSetLoad()
            return True
        except ps.SpinnakerException as ex:
            logging.info('Error: %s' % ex)
            return False
    
    @thread
    def acquisition(self, 
                    num_images:int=10, 
                    wait_time:float=0, 
                    pixelformat:str=None, 
                    fileformat:str=None, 
                    filename:str=None, 
                    folder:str=None, 
                    tag:str=None) -> bool:
        
        result = False
        # update args
        if pixelformat is not None:
            self.pixelformat = pixelformat
        if fileformat is not None:
            self.fileformat = fileformat
        if filename is not None:
            self.filename = filename
        if folder is not None:
            self.folder = folder
        
        cam, cam_list, system = self.find_camera()
        if cam is None:
            logging.info('Camera is not available to set configurations.')
            return False
        
        cam.Init()
        nodemap, tldevice_nodemap = self.nodemap(cam)
        if nodemap is None:
            logging.info('Camera is not available to set configurations.')
            return False
        
        self.config_trigger(nodemap)
        self.config_fomat(nodemap)
        self.update_camera_config(nodemap)

        logging.info('=========== camera acquisition starts ===========')
        cam.BeginAcquisition()

        device_serial_number = '' or self.get_config(tldevice_nodemap, 'DeviceSerialNumber')
        logging.info('Device serial number: %s' % device_serial_number)
        
        # Create ImageProcessor instance for post processing images
        processor = ps.ImageProcessor()
        # By default, if no specific color processing algorithm is set, the image
        # processor will default to NEAREST_NEIGHBOR method.
        processor.SetColorProcessing(ps.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        
        for i in range(num_images): 
            try:
                image_result = cam.GetNextImage(1000)
                if image_result.IsIncomplete():
                    logging.info('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                else:
                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    logging.info('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

                    # Convert image
                    if self.pixelformat == "Mono8":
                        image_converted = processor.Convert(image_result, ps.PixelFormat_Mono8)
                    elif self.pixelformat == "Mono10":
                        image_converted = processor.Convert(image_result, ps.PixelFormat_Mono10)
                    elif self.pixelformat == "Mono12":
                        image_converted = processor.Convert(image_result, ps.PixelFormat_Mono12)
                    
                    # Save image
                    if not os.path.exists(self.folder):
                        os.makedirs(self.folder)
                    
                    timestr = time.strftime("%Y%m%d")
                    image_filename = os.path.join(self.folder, timestr + '_' + self.filename + '_' + str(i) + '_' + self.tag + '.{}'.format(self.fileformat))
                    image_converted.Save(image_filename)
                    logging.info('Image saved at %s' % image_filename)

                    # Release image
                    image_result.Release()
                    logging.info('Image %d released.' % i)

                    # Wait
                    time.sleep(wait_time)
                    result = True

            except ps.SpinnakerException as ex:
                logging.info('Error: %s' % ex)
                result = False

        cam.EndAcquisition()
        
        self.close(cam, cam_list, system)
        return result


# class CameraController:
#     def __init__(self) -> None:
#         # self.main_controller = main_controller
#         # self.worker = worker
#         # self.camera_view = camera_view
#         self.system = None
#         self.cam_list = None
#         self.version = None
#         self.iface_list = None
#         self.num_interfaces = None
#         self.cam_list = None
#         self.num_cams = 0
#         self.cam = None
#         self.nodemap = None
#         self.nodemap_tldevice = None
#         self.isavailable = False
#         self.device_config={}

#         self.find_camera()
#         if self.isavailable:
#             self.device_info()
    
        
#     def find_camera(self):
#         logging.info('============= find camera =============')
#         self.system = ps.System.GetInstance()
#         self.cam_list = self.system.GetCameras()
#         self.version = self.system.GetLibraryVersion()
#         logging.info('Library version: %d.%d.%d.%d' % (self.version.major, self.version.minor, self.version.type, self.version.build))
    
#         # Interface list 
#         self.iface_list = self.system.GetInterfaces()
#         self.num_interfaces = self.iface_list.GetSize()
#         logging.info('Number of interfaces detected: %i' % self.num_interfaces)
        
#         # Camera list 
#         self.num_cams = self.cam_list.GetSize()
#         logging.info('Number of cameras detected: %i' % self.num_cams)
        
#         # Get camera
#         if self.cam_list:
#             self.cam = self.cam_list.GetByIndex(0)

#             if self.cam is not None:
#                 self.cam.Init()
#                 # Get nodemap
#                 self.nodemap = self.cam.GetNodeMap()
#                 self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
#                 logging.info('Camera is initiated.')
#                 self.isavailable = True
#             else:
#                 logging.info('Camera not found.')
#         else:
#             logging.info('Camera is not connected')

#     def reset_camera(self):
#         """Reset camera to default settings."""
#         if self.cam is not None:
#             self.close()
            
#         logging.info('Resetting camera to default settings...')
#         self.find_camera()
#         self.cam.UserSetSelector.SetValue(ps.UserSetSelector_Default)
#         self.cam.UserSetLoad()

#     @thread
#     def acquisition(self, num_images=10, wait_time=0, pixelformat="Mono8", fileformat='bmp', filename='test', folder='data', tag='background'):
#         """Acquire image."""
        
#         # Create ImageProcessor instance for post processing images
#         processor = ps.ImageProcessor()
#         # By default, if no specific color processing algorithm is set, the image
#         # processor will default to NEAREST_NEIGHBOR method.
#         processor.SetColorProcessing(ps.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        
#         self.cam.BeginAcquisition()
#         logging.info('Camera acquisition starts.')
       
#         for i in range(num_images):
#             try: 
#                 image_result = self.cam.GetNextImage(1000)
#                 if image_result.IsIncomplete():
#                     logging.info('Image incomplete with image status %d ...' % image_result.GetImageStatus())
#                 else:

#                     width = image_result.GetWidth()
#                     height = image_result.GetHeight()
#                     logging.info('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

#                     # Get image data
#                     if pixelformat == "Mono8":
#                         image_converted = processor.Convert(image_result, ps.PixelFormat_Mono8)
#                     # image_data = image_converted.GetData()

#                     # Save image
#                     if not os.path.exists(folder):
#                         os.makedirs(folder)

#                     timestr = time.strftime("%Y%m%d_%H%M%S")
#                     image_filename = os.path.join(folder, timestr + '_' + filename + '_' + str(i) + '_' + tag + '.{}'.format(fileformat))
                    
                    
#                     image_converted.Save(image_filename)
#                     logging.info('Image saved at %s' % image_filename)
#                     # Release image
#                     image_result.Release()
#                     logging.info('Image %d released.' % i)
#                     # Wait
#                     time.sleep(wait_time)

#             except ps.SpinnakerException as ex:
#                 logging.info('Error: %s' % ex)

#         self.cam.EndAcquisition()
#         logging.info('Camera acquisition ends.')
    
#     def close(self):
#         if self.cam: 
#             self.cam.DeInit()
#         del self.cam
#         self.cam_list.Clear()
#         self.iface_list.Clear()
#         self.system.ReleaseInstance()
#         logging.info('Camera controller closed.')

#     def device_info(self):
#         """Print device info."""
#         logging.info('============= device info update =============')
#         node_device_information = ps.CCategoryPtr(self.nodemap_tldevice.GetNode('DeviceInformation'))
#         if ps.IsAvailable(node_device_information) and ps.IsReadable(node_device_information):
#             features = node_device_information.GetFeatures()
#             for feature in features:
#                 node_feature = ps.CValuePtr(feature)
#                 logging.info('%s: %s' % (node_feature.GetName(),
#                                         node_feature.ToString() if ps.IsReadable(feature) else 'Node not readable'))
                
#                 if ps.IsReadable(feature):
#                     self.device_config[node_feature.GetName()] = node_feature.ToString() 
#         else:
#             logging.info('Device control information not available.')
    
#     def config_trigger(self, exposure_time='min', trigger='Line3', trigger_delay=0.0):
#         """Configure trigger."""
#         logging.info('============= config trigger =============')
#         self.set_config('TriggerMode', 'Off')
#         self.set_config('GainAuto', 'Off')
#         self.set_config('TriggerSource', trigger)
#         self.set_config('TriggerSelector', 'FrameStart')
#         self.set_config('TriggerActivation', 'RisingEdge')

#         self.set_config('TriggerDelay', trigger_delay)

#         self.set_config('ExposureMode', 'Timed')
#         self.set_config('ExposureAuto', 'Off')
#         self.set_config('ExposureTime', exposure_time)
#         self.set_config('ExposureAuto', 'Off')
#         self.set_config('TriggerMode', 'On')
#         self.set_config('AcquisitionMode', 'Continuous')
    
#     def config_fomat(self, pixel_format='Mono8'):
#         """Configure image format."""
#         self.set_config('PixelFormat', pixel_format)
      
#     def set_config(self, nodename, value):
#         """Set config node."""
#         node_address = self.nodemap.GetNode(nodename)
   
#         if ps.IsAvailable(node_address):

#             if ps.CEnumerationPtr(node_address).IsValid():
#                 node = ps.CEnumerationPtr(node_address)
#                 node_entry = ps.CEnumEntryPtr(node.GetEntryByName(value))
#                 entry_value = node_entry.GetValue()
                
#                 node.SetIntValue(entry_value)
#                 logging.info('%s set to %s' % (node.GetName(), value))
            
#             elif ps.CIntegerPtr(node_address).IsValid():
#                 node = ps.CIntegerPtr(node_address)

#                 if isinstance(value, str):
#                     if value == 'min':
#                         value = node.GetMin()
#                     elif value == 'max':
#                         value = node.GetMax()
#                     else:
#                         logging.info('Value %s is not valid.' % value)
#                 else:
#                     value = int(value)

#                 if node.GetMin() <= value <= node.GetMax():
#                     node.SetValue(value)
#                     logging.info(f'{node.GetName()} set to {value}')
#                 else:
#                     logging.info('Value %s is out of range.' % value)
            
#             elif ps.CFloatPtr(node_address).IsValid():
#                 node = ps.CFloatPtr(node_address)

#                 if isinstance(value, str):
#                     if value == 'min':
#                         value = node.GetMin()
#                     elif value == 'max':
#                         value = node.GetMax()
#                     else:
#                         logging.info('Value %s is not valid.' % value)
#                 else:
#                     value = int(value)

#                 if node.GetMin() <= value <= node.GetMax():
#                     node.SetValue(value)
#                     logging.info(f'{node.GetName()} set to {value}')
#                 else:
#                     logging.info('Value %s is out of range.' % value)

#             elif ps.CBooleanPtr(node_address).IsValid():
#                 node = ps.CBooleanPtr(node_address)
                
#                 value = bool(value)
#                 node.SetValue(value)
#                 logging.info('%s set to %s' % (node.GetName(), value))
#             else:
#                 logging.info('Type of node is not supported temporarily.')
#         else:
#             logging.info('Node %s is not available' % nodename)
        
#     def get_config(self, nodename) -> None:
#         """Get config node."""
#         node_address = self.nodemap.GetNode(nodename)
        
#         if ps.IsAvailable(node_address):
#             # Enumeration node
#             if ps.CEnumerationPtr(node_address).IsValid():
#                 node = ps.CEnumerationPtr(node_address)
#                 node_feature = node.GetCurrentEntry()
                
#                 if ps.IsReadable(node):
#                     node_feature_symbol = node_feature.GetSymbolic()
#                     logging.info('%s: %s' % (node.GetName(), node_feature_symbol))
#                     return node_feature_symbol
#                 else:
#                     logging.info('(Enumeration)Unable to get %s' % node.GetName())

#             # Integer node
#             elif ps.CIntegerPtr(node_address).IsValid():
#                 node = ps.CIntegerPtr(node_address)
#                 node_feature = node.GetValue()
                
#                 if ps.IsReadable(node):
#                     logging.info('%s: %s' % (node.GetName(), node_feature))
#                     return node_feature
#                 else:
#                     logging.info('(Int)Unable to get %s' % node.GetName())
            
#             # Float node
#             elif ps.CFloatPtr(node_address).IsValid():
#                 node = ps.CFloatPtr(node_address)
#                 node_feature = node.GetValue()

#                 if ps.IsReadable(node):
#                     logging.info('%s: %s' % (node.GetName(), node_feature))
#                     return node_feature
#                 else:
#                     logging.info('(Float)Unable to get %s' % node.GetName())
            
#             # Boolean node
#             elif ps.CBooleanPtr(node_address).IsValid():
#                 node = ps.CBooleanPtr(node_address)
#                 node_feature = node.GetValue()

#                 if ps.IsReadable(node):
#                     logging.info('%s: %s' % (node.GetName(), node_feature))
#                     return node_feature
#                 else:
#                     logging.info('(Bool)Unable to get %s' % node.GetName())

#             elif ps.CCommandPtr(node_address).IsValid():
#                 logging.info('Command node is not supported temporarily.')
#             elif ps.CStringPtr(node_address).IsValid():
#                 logging.info('String node is not supported temporarily.')
#             elif ps.CRegisterPtr(node_address).IsValid():
#                 logging.info('Register node is not supported temporarily.')
#             elif ps.CCategoryPtr(node_address).IsValid():
#                 logging.info('Category node is not supported temporarily.') 
#         else: 
#             logging.info('%s node address is not available' % nodename)
