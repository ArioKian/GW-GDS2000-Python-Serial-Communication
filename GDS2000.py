import sys
import numpy as np 
import serial
from serial.tools import list_ports

class GDS_2204:

    standardBaudRates = [50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800, 9600, 19200, 38400, 57600, 115200]
    displayAccumulateModeParams = ['Disable', 'Enable']
    displayWaveformTypeParams = ['Vectors', 'Dots']
    displayGraticuleTypeParams = ['FullGrid', 'CrossType', 'OuterFrame']
    channelNumParams = [1, 2, 3, 4]
    memoryLengthParams = ['MIN', 'MAX']
    timeDivScaleParams = [1e-9, 2.5e-9, 5e-9, 10e-9, 25e-9, 50e-9, 100e-9, 250e-9, 500e-9, 1e-6, 2.5e-6, 5e-6, 10e-6, 25e-6, 50e-6, 100e-6, 250e-6, 500e-6, 1e-3, 2.5e-3, 5e-3, 10e-3, 25e-3, 50e-3, 100e-3, 250e-3, 500e-3, 1, 2.5, 5, 10]
    voltDivScaleParams = [0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5]
    couplingModeParams = ['AC', 'DC', 'GND']
    triggerSourceParams = ['Channel1', 'Channel2', 'Channel3', 'Channel4', 'Extenal', 'AC_Line']
    triggerTypeParams = ['Edge', 'Video', 'Pulse', 'Delay']
    triggerCouplingModeParams = ['AC', 'DC']
    triggerModeParams = ['AutoLevel', 'Auto', 'Normal', 'Single']

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

    def AutoSet(self):
        if(self.connectionStatus):
            self.serialPort.write(b':AUToset\n')
            print(f"INFO: Oscope going under AutoSet Operation.")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")

## Select the accumulate display mode.
    def SetDisplay_AccumulateMode(self, mode):
        if(self.connectionStatus):
            match mode:
                case 'Enable':
                    cmd= f':DISPlay:ACCumulate 1\n'
                case 'Disable':
                    cmd= f':DISPlay:ACCumulate 0\n'
                case _:
                    sys.exit(f"ERROR: the value entered for display accumulate mode is not correct. the correct values are {self.displayAccumulateModeParams}. you passed {mode}")
            checkCmd= f':DISPlay:ACCumulate?\n' ## self.serialPort.write(b':DISPlay:ACCumulate?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: display accumulate mode is set to {self.displayAccumulateModeParams[int(response)]}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")

## Select the dots (or vectors) display for data.points.
    def SetDisplay_WaveformType(self, typ):
        if(self.connectionStatus):
            match typ:
                case 'Vectors':
                    cmd= f':DISPlay:WAVeform 0\n'
                case 'Dots':
                    cmd= f':DISPlay:WAVeform 1\n'
                case _:
                    sys.exit(f"ERROR: the value entered for display waveform type is not correct. the correct values are {self.displayWaveformTypeParams}. you passed {typ}")
            checkCmd= f':DISPlay:WAVeform?\n' ## self.serialPort.write(b':DISPlay:WAVeform?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: display waveform type is set to {self.displayWaveformTypeParams[int(response)]}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")

## Select graticule display type for LCD screen.
    def SetDisplay_GraticuleType(self, typ):
        if(self.connectionStatus):
            match typ:
                case 'FullGrid':
                    cmd= f':DISPlay:GRATicule 0\n'
                case 'CrossType':
                    cmd= f':DISPlay:GRATicule 1\n'
                case 'OuterFrame':
                    cmd= f':DISPlay:GRATicule 2\n'
                case _:
                    sys.exit(f"ERROR: the value entered for display graticule type is not correct. the correct values are {self.displayGraticuleTypeParams}. you passed {typ}")
            checkCmd= f':DISPlay:GRATicule?\n' ## self.serialPort.write(b':DISPlay:GRATicule?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: display graticule type is set to {self.displayGraticuleTypeParams[int(response)]}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")


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

## Sets the horizontal timebase scale per division (SEC/DIV).
    def SetTimeDivScale(self, timDiv):
        if(self.connectionStatus):
            if(timDiv in self.timeDivScaleParams):
                cmd= f':TIMebase:SCALe {float(timDiv)}\n'  ## self.serialPort.write(b':TIMebase:SCALe 500e-6\n')
                checkCmd= f':TIMebase:SCALe?\n' ## self.serialPort.write(b':TIMebase:SCALe?\n')
                self.serialPort.write(cmd.encode('ascii'))
                self.serialPort.write(checkCmd.encode('ascii'))
                response = self.serialPort.readline().decode().strip()
                print(f"INFO: Time/Div scale is set to {response}")
            else:
                sys.exit(f"ERROR: the value entered as Time/Div scale is not correct. The correct values are {self.timeDivScaleParams}. You passed {timDiv}.")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")

## Sets the horizontal position (delay timebase) parameter.
    def SetHorizontalPosition(self, delay):
        if(self.connectionStatus):
            cmd= f':TIMebase:DElay {float(delay)}\n'  ## self.serialPort.write(b':TIMebase:DElay 2.940E-3\n')
            checkCmd= f':TIMebase:DElay?\n' ## self.serialPort.write(b':TIMebase:DElay?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: Time horizontal position offset is set to {response}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   

    def SetChannel_VoltDivScale(self, channelNum, vltDiv):
        if(self.connectionStatus):
            if(channelNum in self.channelNumParams):
                if(vltDiv in self.voltDivScaleParams):
                    cmd= f':CHANnel{channelNum}:SCALe {float(vltDiv)}\n'  ## self.serialPort.write(b':CHANnel1:SCALe 0\n')
                    checkCmd= f':CHANnel{channelNum}:SCALe?\n' ## self.serialPort.write(b':CHANnel1:SCALe?\n')
                    self.serialPort.write(cmd.encode('ascii'))
                    self.serialPort.write(checkCmd.encode('ascii'))
                    response = self.serialPort.readline().decode().strip()
                    print(f"INFO: Channel {channelNum} Volt/Div scale is set to {response}")
                else:
                    sys.exit(f"ERROR: the value entered as Volt/Div for channel {channelNum} is not coorect. The correct values are {self.voltDivScaleParams}. You passed {vltDiv}.")
            else:
                sys.exit(f"ERROR: the value entered as channelNum is out of range. The correct values are {self.channelNumParams}. You passed {channelNum}.")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")

    def SetChannel_PositionOffset(self, channelNum, offset):
        if(self.connectionStatus):
            if(channelNum in self.channelNumParams):
                cmd= f':CHANnel{channelNum}:OFFSet {float(offset)}\n'  ## self.serialPort.write(b':CHANnel1:OFFSet 0\n')
                checkCmd= f':CHANnel{channelNum}:OFFSet?\n' ## self.serialPort.write(b':CHANnel1:OFFSet?\n')
                self.serialPort.write(cmd.encode('ascii'))
                self.serialPort.write(checkCmd.encode('ascii'))
                response = self.serialPort.readline().decode().strip()
                print(f"INFO: Channel {channelNum} position offset is set to {response}")
            else:
                sys.exit(f"ERROR: the value entered as channelNum is out of range. The correct values are {self.channelNumParams}. You passed {channelNum}.")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")

    def SetChannel_CouplingMode(self, channelNum, mode):
        if(self.connectionStatus):
            if(channelNum in self.channelNumParams):
                match mode:
                    case 'AC':
                        cmd= f':CHANnel{channelNum}:COUPling 0\n'  ## self.serialPort.write(b':CHANnel1:COUPling 1\n')
                    case 'DC':
                        cmd= f':CHANnel{channelNum}:COUPling 1\n'
                    case 'GND':
                        cmd= f':CHANnel{channelNum}:COUPling 2\n'
                    case _:
                        sys.exit(f"ERROR: the value entered as coupling mode for channel {channelNum} is out of range. The correct values are {self.couplingModeParams}. You passed {mode}.")            
                checkCmd= f':CHANnel{channelNum}:COUPling?\n' ## self.serialPort.write(b':CHANnel1:COUPling?\n')
                self.serialPort.write(cmd.encode('ascii'))
                self.serialPort.write(checkCmd.encode('ascii'))
                response = self.serialPort.readline().decode().strip()
                print(f"INFO: Channel {channelNum} coupling mode is set to {self.couplingModeParams[int(response)]}")
                # print(f"INFO: Channel {channelNum} coupling mode is set to {response}")
            else:
                sys.exit(f"ERROR: the value entered as channelNum is out of range. The correct values are {self.channelNumParams}. You passed {channelNum}.")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")


## Select and query the trigger source.    
    def SetTrigger_Source(self, source):
        if(self.connectionStatus):
            match source:
                case 'Channel1':
                    cmd= f':TRIGger:SOURce 0\n'  ## self.serialPort.write(b':TRIGger:SOURce 0\n')
                case 'Channel2':
                    cmd= f':TRIGger:SOURce 1\n'  ## self.serialPort.write(b':TRIGger:SOURce 1\n')
                case 'Channel3':
                    cmd= f':TRIGger:SOURce 2\n'  ## self.serialPort.write(b':TRIGger:SOURce 2\n')
                case 'Channel4':
                    cmd= f':TRIGger:SOURce 3\n'  ## self.serialPort.write(b':TRIGger:SOURce 3\n')
                case 'External':
                    cmd= f':TRIGger:SOURce 4\n'  ## self.serialPort.write(b':TRIGger:SOURce 4\n')
                case 'AC_Line':
                    cmd= f':TRIGger:SOURce 5\n'  ## self.serialPort.write(b':TRIGger:SOURce 5\n')
                case _:
                    sys.exit(f"ERROR: the value entered for trigger source is not correct. the correct values are {self.triggerSourceParams}. you passed {source}")
            checkCmd= f':TRIGger:SOURce?\n' ## self.serialPort.write(b':TRIGger:SOURce?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: Trigger source is set to {self.triggerSourceParams[int(response)]}")
            # print(f"INFO: Trigger source is set to {response}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   

## Select and query the trigger type.
    def SetTrigger_Type(self, trigType):
        if(self.connectionStatus):
            match trigType:
                case 'Edge':
                    cmd= f':TRIGger:TYPe 0\n'  ## self.serialPort.write(b':TRIGger:TYPe 0\n')
                case 'Video':
                    cmd= f':TRIGger:TYPe 1\n'  ## self.serialPort.write(b':TRIGger:TYPe 1\n')
                case 'Pulse':
                    cmd= f':TRIGger:TYPe 2\n'  ## self.serialPort.write(b':TRIGger:TYPe 2\n')
                case 'Delay':
                    cmd= f':TRIGger:TYPe 3\n'  ## self.serialPort.write(b':TRIGger:TYPe 3\n')
                case _:
                    sys.exit(f"ERROR: the value entered for trigger type is not correct. the correct values are {self.triggerTypeParams}. you passed {trigType}")
            checkCmd= f':TRIGger:TYPe?\n' ## self.serialPort.write(b':TRIGger:TYPe?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: Trigger type is set to {self.triggerTypeParams[int(response)]}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   

## Select and query the type of trigger coupling.
    def SetTrigger_CouplingMode(self, mode):
        if(self.connectionStatus):
            match mode:
                case 'AC':
                    cmd= f':TRIGger:COUPle 0\n'  ## self.serialPort.write(b':TRIGger:COUPle 0\n')
                case 'DC':
                    cmd= f':TRIGger:COUPle 1\n'  ## self.serialPort.write(b':TRIGger:COUPle 1\n')
                case _:
                    sys.exit(f"ERROR: the value entered as trigger coupling mode is not correct. The correct values are {self.triggerCouplingModeParams}. You passed {mode}.")
            checkCmd= f':TRIGger:COUPle?\n' ## self.serialPort.write(b':TRIGger:COUPle?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: Trigger coupling mode is set to {self.triggerCouplingModeParams[int(response)]}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   

## Select and query the trigger level.
    def SetTrigger_Level(self, level):
        if(self.connectionStatus):
            cmd= f':TRIGger:LEVel {float(level)}\n'  ## self.serialPort.write(b'::TRIGger:LEVel 1.6\n')
            checkCmd= f':TRIGger:LEVel?\n' ## self.serialPort.write(b':TRIGger:LEVel?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: trigger level is set to {response}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   

## Select and query the trigger mode.
    def SetTrigger_Mode(self, mode):
        if(self.connectionStatus):
            match mode:
                case 'Auto Level':
                    cmd= f':TRIGger:MODe 0\n'  ## self.serialPort.write(b':TRIGger:MODe 0\n')
                case 'Auto':
                    cmd= f':TRIGger:MODe 1\n'
                case 'Normal':
                    cmd= f':TRIGger:MODe 2\n'
                case 'Single':
                    cmd= f':TRIGger:MODe 3\n'
                case _:
                    sys.exit(f"ERROR: the value entered as trigger mode is out of range. The correct values are {self.triggerModeParams}. You passed {mode}.")
            checkCmd= f':TRIGger:MODe?\n' ## self.serialPort.write(b':TRIGger:MODe?\n')
            self.serialPort.write(cmd.encode('ascii'))
            self.serialPort.write(checkCmd.encode('ascii'))
            response = self.serialPort.readline().decode().strip()
            print(f"INFO: trigger mode is set to {self.triggerModeParams[int(response)]}")
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   


########################################################################################################
########################################################################################################


########################################################################################################
############################  Methods for the Oscilloscope Operations  ###########################

    def Run(self):
        if(self.connectionStatus):
            cmd = ':RUN\n'
            self.serialPort.write(cmd.encode('ascii'))
            print(f'INFO: oscope in RUN mode')
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   

    def Stop(self):
        if(self.connectionStatus):
            cmd = ':STOP\n'
            self.serialPort.write(cmd.encode('ascii'))
            print(f'INFO: oscope in STOP mode')
        else:
            sys.exit(f"ERROR: No Connection with Oscope or COM port. connectionStatus: {self.connectionStatus}")   

########################################################################################################
########################################################################################################
