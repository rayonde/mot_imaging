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
        self.iface_list = None
        self.cam_list = None
        self.cam = None
        self.nodemap = None
        self.nodemap_tldevice = None

        self.num_interfaces = 0
        self.version = None
        self.num_cams = 0
        self.isavailable = False
        self.device_config={}

        self.find_camera()
        if self.isavailable:
            self.device_info()
    
        
    def find_camera(self) -> bool:
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
                return True
            else:
                logging.info('Camera not found.')
                return False
        else:
            logging.info('Camera is not connected')
            return False

    def reset_camera(self):
        """Reset camera to a normal state by turning off trigger mode"""
        try:
            self.cam.EndAcquisition()
            self.set_config('TriggerMode', 'Off')
            result = True
        except ps.SpinnakerException as ex:
            print('Error: %s' % ex)
            result = False
        return result
        
    @thread
    def acquisition(self, 
                    num_images:int=10, 
                    wait_time:float=0.0, 
                    pixelformat:str="Mono8", 
                    fileformat:str='bmp', 
                    filename:str='test', 
                    folder:str='data', 
                    tag:str="1"):
        """Acquire image."""
        
        # Create ImageProcessor instance for post processing images
        processor = ps.ImageProcessor()
        # By default, if no specific color processing algorithm is set, the image
        # processor will default to NEAREST_NEIGHBOR method.
        processor.SetColorProcessing(ps.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        
        # create folder
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        self.cam.BeginAcquisition()
        logging.info('============ Camera acquisition starts ===========')
       
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

                    timestr = time.strftime("%Y%m%d")
                    image_filename = os.path.join(folder, timestr + '_' + filename + '_' + str(i) + '_' + tag + '.{}'.format(fileformat))
                    
                    
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
        logging.info('============= Camera acquisition ends ============')
    
    def close(self, timeout:float=0.0) -> bool:
        
        result = False
        start_time = time.time()

        if self.cam: 
            while True:
                try:
                    self.cam.DeInit()
                    result = True
                    break
                except ps.SpinnakerException as ex:
                    logging.info('Error: %s' % ex)
                    if time.time() - start_time > timeout:
                        logging.info('Camera deinitiation timeout.')
                        break
                    else:
                        continue        
                # when the camera is streaming, it cannot be deinitiated
                # in this case, the camera list and interface list and system
                # should not be released. 
            if result:              
                del self.cam
                self.cam_list.Clear()
                self.iface_list.Clear()
                self.system.ReleaseInstance()
                logging.info('Camera controller closed.')
                return True
            else:
                return False
        else:
            self.cam_list.Clear()
            self.iface_list.Clear()
            self.system.ReleaseInstance()
            logging.info('Camera is not found, camera controller closed.')
            return True 

        
    def device_info(self):
        """Print device info."""
        logging.info('=============== device info update ===============')
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
    
    def config_trigger(self, 
                       exposure_time:float=0.0, 
                       trigger_source:str='Line0', 
                       trigger_delay:float=0.0) -> bool:
        """Configure trigger."""
        logging.info('================= config trigger =================')
        self.set_config('TriggerMode', 'Off')

        self.set_config('GainAuto', 'Off')
        self.set_config('GammaEnable', 'False')
        self.set_config('TriggerSource', trigger_source)
        self.set_config('TriggerActivation', 'RisingEdge')
        self.set_config('TriggerDelay', trigger_delay)
        self.set_config('ExposureMode', 'Timed')
        self.set_config('ExposureAuto', 'Off')
        self.set_config('ExposureTime', exposure_time)
        # For different camera, the trigger selector may be different
        # For Firefly FFY-U3-16S2M, the trigger selector can be "FrameStart" or "AcquisitionStart
        # self.set_config('TriggerSelector', 'ExposureStart')
        

        # After setting the trigger mode, there will be a error message as below:
        # Error: Spinnaker: Failed waiting for EventData on NEW_BUFFER_DATA event. [-1011]
        # Not sure if it is a problem because there is no physical trigger connected to the camera when
        # the error message appears.
        # The Acquisiton of images has a timeout of 1000 ms, which is set in the acquisition function.

        self.set_config('TriggerMode', 'On')
        self.set_config('AcquisitionMode', 'Continuous')

        self.device_info()
        return True
    
    def config_fomat(self, pixel_format:str='Mono8'):
        """Configure image format."""
        self.set_config('PixelFormat', pixel_format)
      
    def set_config(self, nodename, value):
        """Set config node."""

        node_address = self.nodemap.GetNode(nodename)
   
        if ps.IsAvailable(node_address):
      
            if ps.CEnumerationPtr(node_address).IsValid():
                node = ps.CEnumerationPtr(node_address)
                node_entry = node.GetEntryByName(value)
                if not ps.IsReadable(node_entry):
                    logging.info('Unable to set %s to %s' % (node.GetName(), value))
                    return False
                
                node.SetIntValue(node_entry.GetValue())
                logging.info('%s set to %s' % (node.GetName(), value))
                return True
            
            elif ps.CIntegerPtr(node_address).IsValid():
                node = ps.CIntegerPtr(node_address)
                minvalue = node.GetMin()
                maxvalue = node.GetMax()
                
                try: 
                    value = int(value)
                except ValueError:
                    logging.info('Value %s is not valid.' % value)
                    return False
            
                if minvalue <= value <= maxvalue:
                    node.SetValue(value)
                    logging.info(f'{node.GetName()} set to {value}')
                    return True
                elif value < minvalue:
                    node = node.SetValue(minvalue)
                    logging.info(f'{node.GetName()} set to minimal value {minvalue}')
                    return True
                elif value > maxvalue:
                    node = node.SetValue(maxvalue)
                    logging.info(f'{node.GetName()} set to maximal value {maxvalue}')
                    return True
            
            elif ps.CFloatPtr(node_address).IsValid():
                node = ps.CFloatPtr(node_address)
                minvalue = node.GetMin()
                maxvalue = node.GetMax()

                try:
                    value = float(value)
                except ValueError:
                    logging.info('Value %s is not valid.' % value)
                    return False
                
                if minvalue <= value <= maxvalue:
                    node.SetValue(value)
                    logging.info(f'{node.GetName()} set to {value}')
                    return True
                elif value < minvalue:
                    node.SetValue(minvalue)
                    logging.info(f'{node.GetName()} set to minimal value {minvalue}')
                    return True
                elif value > maxvalue:
                    node.SetValue(maxvalue)
                    logging.info(f'{node.GetName()} set to maximal value {maxvalue}')
                    return True

            elif ps.CBooleanPtr(node_address).IsValid():
                node = ps.CBooleanPtr(node_address)
                
                try:
                    value = bool(value)
                except ValueError:
                    logging.info('Value %s is not valid.' % value)
                    return False
                
                node.SetValue(value)
                logging.info('%s set to %s' % (node.GetName(), value))
                return True
                
            else:
                logging.info('Type of node is not supported temporarily.')
                return False
        else:
            logging.warning('Node %s is not available' % nodename)
            return False
        
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
            
            # other node 
            else:
                logging.info('Type of node is not supported temporarily.')
                return None

            
        else: 
            logging.info('%s node address is not available' % nodename)
            return None
