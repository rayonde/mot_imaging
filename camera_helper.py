from platform import node
import PySpin
import os
import sys
import time 
import logging

class Interface():
    def __init__(self):
        self.system = PySpin.System.GetInstance()
        self.version =self.system.GetLibraryVersion()
        logging.info('Library version: %d.%d.%d.%d' % (self.version.major, self.version.minor, self.version.type, self.version.build))
    
        # Interface list 
        self.iface_list = self.system.GetInterfaces()
        self.num_interfaces = self.iface_list.GetSize()
        logging.info('Number of interfaces detected: %i' % self.num_interfaces)
    
        # Camera list 
        self.cam_list = self.system.GetCameras()
        self.num_cams = self.cam_list.GetSize()
        logging.info('Number of cameras detected: %i' % self.num_cams)

    def __enter__(self):
        # Finish if there are no cameras
        if self.num_cams == 0 or self.num_interfaces == 0:
            logging.info('No camera is detected!')
            raise Exception("No camera is connected")
        else: 
            return self
     
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.cam_list.Clear()
        self.iface_list.Clear()
        self.system.ReleaseInstance()
        print('Camera has been closed!')
        input('Done! Press Enter to exit...')

def print_device_info(nodemap):
    """
    This function prints the device information of the camera from the transport
    layer
    """
    print('**************************')
    print('*** DEVICE INFORMATION ***\n')

    try:
        node_device_information = PySpin.CCategoryPtr(nodemap.GetNode('DeviceInformation'))

        if PySpin.IsAvailable(node_device_information) and PySpin.IsReadable(node_device_information):
            features = node_device_information.GetFeatures()
            for feature in features:
                node_feature = PySpin.CValuePtr(feature)
                print('%s: %s' % (node_feature.GetName(),
                                  node_feature.ToString() if PySpin.IsReadable(node_feature) else 'Node not readable'))
            return True
        else:
            print('Device control information not available.')
            return False
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        return False

def get_entry(nodemap, nodename):
    try: 
        node = PySpin.CEnumerationPtr(nodemap.GetNode(nodename))
        print('%s' % nodename, node.GetEntries())
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

def get_parameter(nodemap, nodename):
    try: 
        node = PySpin.CEnumerationPtr(nodemap.GetNode(nodename))
        if PySpin.IsAvailable(node):
            print('%s : %s' % (nodename, node.GetCurrentEntry().GetSymbolic()))
        else: 
            print('%s is not available' % nodename)
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False
  
def set_parameter(nodemap, nodename, entryname) -> bool:
    try: 
        node = PySpin.CEnumerationPtr(nodemap.pri(nodename))
        if not PySpin.IsAvailable(node) or not PySpin.IsWritable(node):
            print('Unable to set %s (enum retrieval). Aborting...' % nodename)
            return False
        
        else: 
            # Retrieve entry node from enumeration node
            node_entry = PySpin.CEnumEntryPtr(node.GetEntryByName(entryname))

            if not PySpin.IsAvailable(node_entry) or not PySpin.IsReadable(node_entry):
                print('Unable to set %s (enum retrieval) as %s. Aborting...' % (nodename, entryname))
                return False
            else: 
                # Retrieve integer value from entry node
                node_entry_value = node_entry.GetValue()
                
                # Set integer value from entry node as new value of enumeration node
                node.SetIntValue(node_entry_value)
                print('%s set to %s' % (nodename, node.GetCurrentEntry().GetSymbolic()))
                return True
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False
    
def set_numeric_parameter(nodemap, nodename, value) -> bool:
    try:
        node_i = PySpin.CIntegerPtr(nodemap.GetNode(nodename))
        node_f = PySpin.CFloatPtr(nodemap.GetNode(nodename))
        if node_i.IsValid():
            node = node_i
        elif node_f.IsValid():
            node = node_f
        else: 
            print('The type of %s is not a integer or float' % nodename,value)
            return False

        if node_i.IsValid() and (isinstance(value, int) or isinstance(value, float)):
            value = int(value)
            if (value >= node.GetMin()) and (value <= node.GetMax()):
                node.SetValue(value)
                print('%s (integer) set to %i [%i, %i]' % (nodename,value, node.GetMin(), node.GetMax()))
                return True
            else:
                print('%s has minimum %i and maximum %i, assigned value exceeds this interval' % (nodename,node.GetMin, node.GetMax))
                return False

        elif node_f.IsValid() and (isinstance(value, int) or isinstance(value, float)):
            value = float(value)
            if (value >= node.GetMin()) and (value <= node.GetMax()):
                node.SetValue(value)
                print('%s (float) set to %f [%f, %f]' % (nodename,value, node.GetMin(), node.GetMax()))
                return True
            else:
                print('%s has minimum %i and maximum %i, assigned value exceeds this interval' % (nodename,node.GetMin, node.GetMax))
                return False

        elif isinstance(value, str) and value == 'Min':
            node.SetValue(node.GetMin())
            print('%s set to the minimum %i' % (nodename, node.GetMin()))
            return True

        elif isinstance(value, str) and value == 'Max':
            node.SetValue(node.GetMax())
            print('%s set to the maxmum %i' % (nodename, node.GetMax()))
            return True
        else: 
            print('%s is not available...' % nodename)
            return False
    
    except PySpin.SpinnakerException as ex:
        print('Error: %s' % ex)
        result = False

def acquire_images_by_number(cam, nodemap, num_images, pixelformat='mono', filename=None, foldername=None) ->bool:
    """ This function acquires multiple images in continuous mode 
    """
    set_parameter(nodemap,'AcquisitionMode', 'Continuous')
    print('*************************')
    print('*** IMAGE ACQUISITION ***\n')
    

    cam.BeginAcquisition()
    for i in range(num_images):
        try: 
            image_result = cam.GetNextImage(1000)
            if image_result.IsIncomplete():
                    print('Image incomplete with image status %d ...' % image_result.GetImageStatus())
            else:
                width = image_result.GetWidth()
                height = image_result.GetHeight()
                timestr = time.strftime("%Y%m%d_%H%M%S")
                print('Grabbed Image %d, width = %d, height = %d' % (i, width, height))
                
                image_converted = image_result.Convert(PySpin.PixelFormat_Mono16, PySpin.HQ_LINEAR)
            
                if filename and not foldername:
                    name = '%s_%s_%d.bmp' % (timestr, filename, i)
                elif foldername and foldername:
                    name = '%s/%s_%s_%d.bmp' % (foldername, timestr, filename, i)
                elif not foldername and foldername:
                    name = '%s/%s_%d.bmp' % (foldername, timestr, i)
                else: 
                    name = '%s_%d.bmp' % (timestr, i)
                
                image_converted.Save(name)
                print('Image saved at %s' % name)

                image_result.Release()

        except PySpin.SpinnakerException as ex:
                print('Error: %s' % ex)
                return False
    cam.EndAcquisition()
    return True 
 
def configure_trigger(nodemap, trigger_source='Line3'):
    #  The trigger must be disabled in order to configure whether the source is software or hardware.
    set_parameter(nodemap, 'AcquisitionMode', 'Continuous')
    set_parameter(nodemap, 'TriggerMode', 'Off')
    set_parameter(nodemap, 'ExposureAuto', 'Off')
    set_parameter(nodemap, 'ExposureMode', 'Timed')

    # suggest the probe beam TTL trigger signal delays 1us after the camera trigger signal
    set_numeric_parameter(nodemap, 'ExposureTime', 50)
    set_numeric_parameter(nodemap, 'TriggerDelay', 0)
    set_parameter(nodemap, 'TriggerSelector', 'ExposureStart')
    set_parameter(nodemap, 'TriggerActivation', 'RisingEdge')
    # (yellow) Pin9 Line0 Opto-isolated input
    # (green)  Pin4 GPIO3/Line3
    # (purple) Pin45 GPIO2/Line2
    set_parameter(nodemap, 'TriggerSource', 'Line3')
    set_parameter(nodemap, 'TriggerMode', 'On')

def reset_trigger(nodemap):
    set_parameter(nodemap, 'ExposureAuto', 'Off')

if __name__ == '__main__':
    with Interface() as iface:
        cam =  iface.cam_list[0]
        cam.Init()
        nodemap = cam.GetNodeMap()
        nodemap_tldevice = cam.GetTLDeviceNodeMap()
        
        # Set acquisition mode to continuous (required for multiple images)
        # Print device information 
        # print_device_info(nodemap_tldevice)
        
        # In order to access the node entries, they have to be casted to a pointer type (CEnumerationPtr here)
        # set_parameter(nodemap, 'PixelFormat', 'Mono12')
        # set_parameter(nodemap, 'PixelFormat', 'Mono16')
        # set_parameter(nodemap, 'PixelFormat', 'Raw12')
        # set_parameter(nodemap, 'PixelFormat', 'Raw16')
        # get_parameter(nodemap, 'PixelSize')
        # get_parameter(nodemap, 'PixelCoding')
        # set_numeric_parameter(nodemap, 'OffsetX', 'Min')
        # set_numeric_parameter(nodemap, 'OffsetY', 'Min')
        set_parameter(nodemap, 'GainAuto', 'Off')
        set_numeric_parameter(nodemap, 'Gain', 20)
       
        configure_trigger(nodemap)
        set_parameter(nodemap, 'TriggerSelector', 'FrameStart')
         
        #acquire_images_by_number(cam, nodemap, 5, filename='trigger_test', foldername="trigger_test")
        # # cam.BeginAcquisition()
        # # print('Acquiring images...')
        cam.DeInit()
        del cam

    