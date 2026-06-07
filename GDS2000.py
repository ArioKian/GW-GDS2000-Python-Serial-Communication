import sys
import numpy as np 
import serial
from serial.tools import list_ports

class GDS_2204:

    standardBaudRates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
    channelNumParams = [1, 2, 3, 4]
    memoryLengthParams = ['MIN', 'MAX']

    def __init__(self):
        self.connectionStatus = False
        self.serialPort = None

    def List_COMPorts(self):
        for port in list_ports.comports():
            print(port.device, port.description, port.manufacturer, port.product)

########################################################################################################
########################  Methods for Checking Serial Communication Parameters  ######################## 
    def Check_BaudRate(self, baudrate):
        if(baudrate in self.standardBaudRates):
            baudrate = baudrate
        else:
            sys.exit(f"ERROR: the value entered as 'baudrate' for Serial Communication is not correct. The correct values are: {self.standardBaudRates}. You passed:{baudrate}")
        print(f"INFO: 'baudrate' is set as {baudrate}. ")
        return baudrate

    def Check_ByteSize(self, bytesize):
        match bytesize:
            case 5:
                bytesize = serial.FIVEBITS 
            case 6:
                bytesize = serial.SIXBITS
            case 7:
                bytesize = serial.SEVENBITS
            case 8:
                bytesize = serial.EIGHTBITS
            case _:
                sys.exit(f"ERROR: the value entered as 'bytesize' for Serial Communication is not correct. The correct values are: 5, 6, 7, and 8. You passed:{bytesize}")
        print(f"INFO: 'bytesize' is set as {bytesize}. ")
        return bytesize

    def Check_Parity(self, parity):
        match parity:
            case 'NONE':
                parity = serial.PARITY_NONE
            case 'EVEN':
                parity = serial.PARITY_EVEN
            case 'ODD':
                parity = serial.PARITY_ODD
            case 'MARK':
                parity = serial.PARITY_MARK
            case 'SPACE':
                parity = serial.PARITY_SPACE
            case _:
                sys.exit(f"ERROR: the value entered as 'parity' for Serial Communication is not correct. The correct values are: 'NONE', 'EVEN', 'ODD', 'MARK', and 'SPACE'. You passed:{parity}")
        print(f"INFO: 'parity' is set as {parity}. ")
        return parity

    def Check_Stopbits(self, stopbits):
        match stopbits:
            case 1:
                stopbits = serial.STOPBITS_ONE
            case 1.5:
                stopbits = serial.STOPBITS_ONE_POINT_FIVE
            case 2:
                stopbits = serial.STOPBITS_TWO
            case _:
                sys.exit(f"ERROR: the value entered as 'stopbits' for Serial Communication is not correct. The correct values are: 1, 1.5, and 2. You passed:{stopbits}")
        print(f"INFO: 'stopbits' is set as {stopbits}. ")
        return stopbits
########################################################################################################
########################################################################################################
    
    
########################################################################################################
#########################  Methods for Serial Connection with the Oscilloscope  ########################     
    def Check_OscopeConnection(self,):
        self.serialPort.write(b'*IDN?\n')
        response = self.serialPort.readline().decode().strip()
        return response

    def ConnectOscope(self, port, baudrate, bytesize, parity, stopbits, timeout=2):
        baudrate = self.Check_BaudRate(baudrate)
        bytesize = self.Check_ByteSize(bytesize)
        parity = self.Check_Parity(parity)
        stopbits = self.Check_Stopbits(stopbits)
        
        ser= serial.Serial(port=port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
        self.connectionStatus = ser.is_open
        if(self.connectionStatus):
            print(f"INFO: COM port Connected Succesfully.")
            self.serialPort = ser
        else:
            sys.exit(f"ERROR: COM port Connection FAILED.")
        
        response = self.Check_OscopeConnection()
        if(response != None):
            print(f"INFO: Oscope Connected Succesfully: {response}")
        else:
            sys.exit(f"ERROR: Oscope Connection FAILED.")
########################################################################################################
########################################################################################################


########################################################################################################
############################  Methods for the Oscilloscope Initial Settings  ###########################
    def ActivateChannel(self, channelNum):
        if(self.connectionStatus):
            if(channelNum in self.channelNumParams):
                cmd= f':CHANnel{channelNum}:DISPlay 1\n'  ## self.serialPort.write(b':CHANnel1:DISPlay 1\n')
                checkCmd= f':CHANnel{channelNum}:DISPlay?\n' ## self.serialPort.write(b':CHANnel1:DISPlay?\n')
                self.serialPort.write(cmd.encode('ascii'))
                self.serialPort.write(checkCmd.encode('ascii'))
                response = self.serialPort.readline().decode().strip()
                if(response=='1'):
                    print(f"INFO: Channel {channelNum} Activated.")
            else:
                sys.exit(f"ERROR: the value entered as channelNum is out of range. The correct values are {self.channelNumParams}. You passed {channelNum}.")

        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")
    
    def DeactivateChannel(self, channelNum):
        if(self.connectionStatus):
            if(channelNum in self.channelNumParams):
                cmd= f':CHANnel{channelNum}:DISPlay 0\n'  ## self.serialPort.write(b':CHANnel1:DISPlay 0\n')
                checkCmd= f':CHANnel{channelNum}:DISPlay?\n' ## self.serialPort.write(b':CHANnel1:DISPlay?\n')
                self.serialPort.write(cmd.encode('ascii'))
                self.serialPort.write(checkCmd.encode('ascii'))
                response = self.serialPort.readline().decode().strip()
                if(response=='0'):
                    print(f"INFO: Channel {channelNum} Deactivated.")
            else:
                sys.exit(f"ERROR: the value entered as channelNum is out of range. The correct values are {self.channelNumParams}. You passed {channelNum}.")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")

    def SetAcquireMemoryLength(self, length):
        if(self.connectionStatus):
            match length:
                case 'MIN':
                    self.serialPort.write(b':ACQuire:LENgth 0\n')
                case 'MAX':
                    self.serialPort.write(b':ACQuire:LENgth 1\n')
                case _:
                    sys.exit(f"ERROR: the value entered as length is not correct. The Correct Values are 'Min' and 'MAX'. You passed {length}.")
            self.serialPort.write(b':ACQuire:LENgth?\n')
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: Acquire Memory Length is set to {response}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")


    

########################################################################################################
########################################################################################################

