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
        # self.main_controller = main_controller
        # self.worker = worker
        # self.camera_view = camera_view
        self.system = None
        self.cam_list = None
        self.version = None
        self.iface_list = None
        self.num_interfaces = None
        self.cam_list = None
        self.num_cams = 0
        self.cam = None
        self.nodemap = None
        self.nodemap_tldevice = None
        self.isavailable = False
        self.device_config={}

        self.find_camera()
        if self.isavailable:
            self.device_info()
    
        
    def find_camera(self):
        logging.info('============= find camera =============')
        self.system = ps.System.GetInstance()
        self.cam_list = self.system.GetCameras()
        self.version = self.system.GetLibraryVersion()
        logging.info('Library version: %d.%d.%d.%d' % (self.version.major, self.version.minor, self.version.type, self.version.build))
    
        # Interface list 
        self.iface_list = self.system.GetInterfaces()
        self.num_interfaces = self.iface_list.GetSize()
        logging.info('Number of interfaces detected: %i' % self.num_interfaces)
        
        # Camera list 
        self.num_cams = self.cam_list.GetSize()
        logging.info('Number of cameras detected: %i' % self.num_cams)
        
        # Get camera
        if self.cam_list:
            self.cam = self.cam_list.GetByIndex(0)

            if self.cam is not None:
                self.cam.Init()
                # Get nodemap
                self.nodemap = self.cam.GetNodeMap()
                self.nodemap_tldevice = self.cam.GetTLDeviceNodeMap()
                logging.info('Camera is initiated.')
                self.isavailable = True
            else:
                logging.info('Camera not found.')
        else:
            logging.info('Camera is not connected')

    def reset_camera(self):
        """Reset camera to default settings."""
        if self.cam is not None:
            self.close()
            
        logging.info('Resetting camera to default settings...')
        self.find_camera()
        self.cam.UserSetSelector.SetValue(ps.UserSetSelector_Default)
        self.cam.UserSetLoad()

    @thread
    def acquisition(self, num_images=10, wait_time=0, pixelformat="Mono8", fileformat='bmp', filename='test', folder='data', tag='background'):
        """Acquire image."""
        
        # Create ImageProcessor instance for post processing images
        processor = ps.ImageProcessor()
        # By default, if no specific color processing algorithm is set, the image
        # processor will default to NEAREST_NEIGHBOR method.
        processor.SetColorProcessing(ps.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        
        self.cam.BeginAcquisition()
        logging.info('Camera acquisition starts.')
       
        for i in range(num_images):
            try: 
                image_result = self.cam.GetNextImage(1000)
                if image_result.IsIncomplete():
                    logging.info('Image incomplete with image status %d ...' % image_result.GetImageStatus())
                else:

                    width = image_result.GetWidth()
                    height = image_result.GetHeight()
                    logging.info('Grabbed Image %d, width = %d, height = %d' % (i, width, height))

                    # Get image data
                    if pixelformat == "Mono8":
                        image_converted = processor.Convert(image_result, ps.PixelFormat_Mono8)
                    # image_data = image_converted.GetData()

                    # Save image
                    if not os.path.exists(folder):
                        os.makedirs(folder)

                    timestr = time.strftime("%Y%m%d_%H%M%S")
                    image_filename = os.path.join(folder, timestr + filename + '_' + str(i) + '_' + tag + '.{}'.format(fileformat))
                    
                    
                    image_converted.Save(image_filename)
                    logging.info('Image saved at %s' % image_filename)
                    # Release image
                    image_result.Release()
                    logging.info('Image %d released.' % i)
                    # Wait
                    time.sleep(wait_time)

            except ps.SpinnakerException as ex:
                logging.info('Error: %s' % ex)

        self.cam.EndAcquisition()
        logging.info('Camera acquisition ends.')
    
    def close(self):
        self.cam.DeInit()
        del self.cam
        self.cam_list.Clear()
        self.iface_list.Clear()
        self.system.ReleaseInstance()
        logging.info('Camera controller closed.')

    def device_info(self):
        """Print device info."""
        logging.info('============= device info update =============')
        node_device_information = ps.CCategoryPtr(self.nodemap_tldevice.GetNode('DeviceInformation'))
        if ps.IsAvailable(node_device_information) and ps.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = ps.CValuePtr(feature)
                logging.info('%s: %s' % (node_feature.GetName(),
                                        node_feature.ToString() if ps.IsReadable(feature) else 'Node not readable'))
                
                if ps.IsReadable(feature):
                    self.device_config[node_feature.GetName()] = node_feature.ToString() 
        else:
            logging.info('Device control information not available.')
    
    def config_trigger(self, exposure_time='min', trigger='Line3', trigger_delay=0.0):
        """Configure trigger."""
        logging.info('============= config trigger =============')
        self.set_config('TriggerMode', 'Off')
        self.set_config('GainAuto', 'Off')
        self.set_config('TriggerSource', trigger)
        self.set_config('TriggerSelector', 'FrameStart')
        self.set_config('TriggerActivation', 'RisingEdge')

        if trigger_delay>0.0:
            self.set_config('TriggerDelayEnabled', True)
        self.set_config('TriggerDelay', trigger_delay)

        self.set_config('ExposureMode', 'Timed')
        self.set_config('ExposureAuto', 'Off')
        self.set_config('ExposureTime', exposure_time)
        self.set_config('ExposureAuto', 'Off')
        self.set_config('TriggerMode', 'On')
        self.set_config('AcquisitionMode', 'Continuous')
    
    def config_fomat(self, pixel_format='Mono8'):
        """Configure image format."""

        self.set_config('PixelFormat', pixel_format)
      
    def set_config(self, nodename, value):
        """Set config node."""
        node_address = self.nodemap.GetNode(nodename)
   
        if ps.IsAvailable(node_address):

            if ps.CEnumerationPtr(node_address).IsValid():
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
        
    def get_config(self, nodename) -> None:
        """Get config node."""
        node_address = self.nodemap.GetNode(nodename)
        
        if ps.IsAvailable(node_address):
            # Enumeration node
            if ps.CEnumerationPtr(node_address).IsValid():
                node = ps.CEnumerationPtr(node_address)
                node_feature = node.GetCurrentEntry()
                
                if ps.IsReadable(node):
                    node_feature_symbol = node_feature.GetSymbolic()
                    logging.info('%s: %s' % (node.GetName(), node_feature_symbol))
                    return node_feature_symbol
                else:
                    logging.info('(Enumeration)Unable to get %s' % node.GetName())

            # Integer node
            elif ps.CIntegerPtr(node_address).IsValid():
                node = ps.CIntegerPtr(node_address)
                node_feature = node.GetValue()
                
                if ps.IsReadable(node):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('(Int)Unable to get %s' % node.GetName())
            
            # Float node
            elif ps.CFloatPtr(node_address).IsValid():
                node = ps.CFloatPtr(node_address)
                node_feature = node.GetValue()

                if ps.IsReadable(node):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('(Float)Unable to get %s' % node.GetName())
            
            # Boolean node
            elif ps.CBooleanPtr(node_address).IsValid():
                node = ps.CBooleanPtr(node_address)
                node_feature = node.GetValue()

                if ps.IsReadable(node):
                    logging.info('%s: %s' % (node.GetName(), node_feature))
                    return node_feature
                else:
                    logging.info('(Bool)Unable to get %s' % node.GetName())

            elif ps.CCommandPtr(node_address).IsValid():
                logging.info('Command node is not supported temporarily.')
            elif ps.CStringPtr(node_address).IsValid():
                logging.info('String node is not supported temporarily.')
            elif ps.CRegisterPtr(node_address).IsValid():
                logging.info('Register node is not supported temporarily.')
            elif ps.CCategoryPtr(node_address).IsValid():
                logging.info('Category node is not supported temporarily.') 
        else: 
            logging.info('%s node address is not available' % nodename)
