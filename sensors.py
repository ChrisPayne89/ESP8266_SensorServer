import math,supp

# ------------------------- Class SensorMngr --------------------------
# Class handles Sensor-instances
        
class SensorMngr:
    def __init__(self,commServer,IFMngr):
        self.__commServer = commServer
        self.__IFMngr = IFMngr
        self.__sensors = []
        
    def sensorResolve(self,name):
        index = 0
        for sens in self.__sensors:
            sensName = sens.get_name()
            if sensName == name:
                self.__commServer.sendMessage("Resolved sensor: " + name, 2)
                return sens, index
            index = index + 1
        self.__commServer.sendError("Sensor name could not be resolved!")
        return None, None
    
    def sensorExists(self,name):
        for sens in self.__sensors:
            sensName = sens.get_name()
            if sensName == name:
                self.__commServer.sendMessage("Sensor: " + name + " exists.", 2)
                return True
        self.__commServer.sendMessage("Sensor: " + name + " does not exist.", 2)
        return False
    
    def sensorAdd(self,sensData):
        para = []
        value = []
        try:
            sensPara = sensData.split(";")
            for attr in sensPara:
                attrSplit = attr.split("=")
                para.append(attrSplit[0])
                value.append(attrSplit[1])
            if not self.sensorExists(value[para.index('name')]):
                sensModel = value[para.index('model')]
                sensIF = self.__IFMngr.getIF(value[para.index('IF')])
                del(value[para.index('IF')])
                del(para[para.index('IF')])
                if sensModel == 'DS1631Z':
                    sens = Sensor_DS1631Z(commServer=self.__commServer,IF=sensIF,**dict(zip(para,value)))
                if sensModel == 'MAX31865':
                    sens = Sensor_MAX31865(commServer=self.__commServer,IF=sensIF,**dict(zip(para,value)))
                    print('sensorCreated')
                    if sens.connectToSensor():
                        self.__sensors.append(sens)
                        self.__commServer.sendCMD("SensorRegister", str(sens.get_id()) + ";" + sensData)
                        self.__commServer.sendMessage("Sensor '" + sens.get_name() + "' succesfully registered!", 1)
                    else:
                        self.__commServer.sendError("Sensor '" + sens.get_name() + "' could not be registered! Connection to sensor failed!")
                else:
                    self.__commServer.sendError("Sensor '" + sens.get_name() + "' could not be registered! Sensor Model not known!")
                    raise Exception("Sensor type not supported!")
            else:
                self.__commServer.sendError("Sensor '" + value[para.index("name")] + "' could not be registered! Sensor name already exists!")
        except:
            self.__commServer.sendError("An unspecified error occured while adding a sensor!")
            
    def sensorRemove(self,name):
        if name == "All":
            self.__sensors = []
        else:
            try:
                self.__sensors.remove(self.sensorResolve(name)[0])
                self.__commServer.sendCommand("SensorRemove", name)
                self.__commServer.sendMessage("Sensor '" + name + "' succesfully removed!", 1)
            except:
                self.__commServer.sendError("An error occured while removing sensor" + name)
                
    def getSensorValues(self):
        valStr = ""
        for sens in self.__sensors:
            sensName = sens.get_name()
            try:
                val = sens.getValue()
            except:
                val = "88.88"
                pass
            valStr = valStr + sensName + "," + val + ";"
            #print("Fetched Temperature: " + Temperature + " from " + sensName)
        return valStr
    
    def setSimulationMode(self,name,val):
        if name == "All":
            for sens in self.__sensors:
                sens.setSimulationMode(val)
        else:
            self.sensorResolve(name)[0].setSimulationMode(val)
                
    def setSimulationRate(self,name,val):
        if name == "All":
            for sens in self.__sensors:
                sens.setSimulationRate(val)
        else:
            self.sensorResolve(name)[0].setSimulationRate(val)
                
    def resetSimulation(self,name):
        if name == "All":
            for sens in self.__sensors:
                sens.resetSimulation()
        else:
            self.sensorResolve(name)[0].resetSimulation()
                
    def setResolution(self,name,val):
        if name == "All":
            for sens in self.__sensors:
                sens.setResolution(val)
        else:
            self.sensorResolve(name)[0].setResolution(val)
                
    def getCMDByte(self,name):
        if name == "All":
            for sens in self.__sensors:
                sens.readCommandByte()
        else:
            self.sensorResolve(name)[0].readCommandByte()
            
    def resetSensor(self,name):
        if name == "All":
            for sens in self.__sensors:
                sens.resetSensor()
        else:
            self.sensorResolve(name)[0].resetSensor()
            
    def startTempMeasurement(self,name):
        if name == "All":
            for sens in self.__sensors:
                sens.startTempMeasurement()
        else:
            self.sensorResolve(name)[0].startTempMeasurement()
    
    def stopTempMeasurement(self,name):
        if name == "All":
            for sens in self.__sensors:
                sens.stopTempMeasurement()
        else:
            self.sensorResolve(name)[0].stopTempMeasurement()
            
    def readTemp(self,name):
        if name == "All":
            for sens in self.__sensors:
                sens.readTemp()
        else:
            self.sensorResolve(name)[0].readTemp()
        
    
# ------------------------- End of SensorMngr --------------------------

# ------------------------- Class Sensor --------------------------
# Top-level class of any sensor

class Sensor:
    def __init__(self, commServer, IF, name, model, simulationMode):
        self.__commServer = commServer
        self.__id = 0
        self._simCount = 0
        self._simRate = 0.1
        self._name = name
        self.__model = model
        self.__IF = IF
        if simulationMode == None:
            self._simulationMode = False
        else:
            self._simulationMode = supp.getBool(simulationMode)
            
    def getValue(self):
        # Method has to be implemented by each sensor and tailored to the specific reading routine
        raise Exception("No data acquisition routine defined!") 
            
    def get_name(self):
        return self._name
    
    def get_model(self):
        return self.__model
    
    def get_IF(self):
        return self._IF
    
    def get_id(self):
        return self.__id
    
    def get_simulationMode(self):
        return self._simulationMode
 
    def setSimulationMode(self, simMode):
        self._simulationMode = simMode
        
    def setSimulationRate(self,simRate):
        self._simRate = simRate
    
    def resetSimulation(self):
        self._simCount = 0
        
    def reportError(self, text):
        self.__commServer.sendError(self.get_name() + ": " + text)
        
    def reportMessage(self, text):
        self.__commServer.sendMessage(self.get_name() + ": " + text, 1)
        
# ------------------------- End of Sensor --------------------------

# ------------------------- Class Temp Sensor --------------------------
# Top-level class of any temperature sensor

class SensorTemp(Sensor):
    def __init__(self, commServer, IF, name, model, simulationMode, tempRange):
        Sensor.__init__(self, commServer, IF, name, model, simulationMode)
        try:
            self.setSensorTemp(tempRange)
        except:
            self.reportError("Temperature range for sensor set to the default limits (-10 100)C")
            self.__tempRange = [-10, 100]
    
    def setSensorTemp(self, tempRange):
        tempRange = tempRange[1:-1].split(",")
        if len(tempRange) == 2:
            try:
                temp1 = int(tempRange[0]) # Type-cast to check for valid argument (int-type)
                temp2 = int(tempRange[1])
            except:
                temp1 = 0
                temp2 = 0
                self.reportError("Argument for temperature range has to be of type 'int'")
            if temp1 < temp2:
                self.__tempRange = tempRange
            else:
                self.reportError("The minimum of the temperature range has to be smaller than the maximum!")
                raise TypeError()
        else:
            self.reportError("Please specify a list of 2 elements containing the valid temperature range")
            raise TypeError()
            
    def get_tempRange(self):
        return self.__tempRange

# ------------------------- End of Temp Sensor --------------------------

# ------------------------- Class Temp Sensor DS1631Z --------------------------
# Temperature sensor from Maxim Integrated

class Sensor_DS1631Z(SensorTemp):
    def __init__(self, commServer, IF, name, model, simulationMode, tempRange, address):
        SensorTemp.__init__(self, commServer, IF, name, model, simulationMode, tempRange)
        self.setSensorSO8(address)
    
    def setSensorSO8(self, address):
        self.__address = address
        
    def connectToSensor(self):
        if self._simulationMode:
            return True
        else:
            try:
                sens = smbus.SMBus(1)
                sens.write_byte(self.__address, 0x51)
                self.__sens = sens
                self.reportMessage("Connection to sensor established.")
                return True
            except:
                self.reportError("Connection to sensor failed!")
                return False
        
    def getValue(self):
        if self._simulationMode:
            self._simCount = self._simCount + self._simRate
            return '{:.2f}'.format(20*math.sin(math.pi*self._simCount))
        else:
            try:
                x = self.__sens.read_word_data(self.__address, 0xAA)
                
                highValue = x & 0x00FF
                lowValue = (x >> 8) & 0x00FF
                
                if highValue & 0x80:
                    highValue=-(((~highValue) & 0xFF)+1)
                    trest = 0
                    lowValue=(~lowValue)+1
                    if lowValue & 0x80:
                        trest=trest+0.5
                    if lowValue & 0x40:
                        trest=trest+0.250
                    if lowValue & 0x20:
                        trest=trest+0.125
                    if lowValue & 0x10:
                        trest=trest+0.0625
                else:
                    trest=0
                    if lowValue & 0x80:
                        trest=trest+0.5
                    if lowValue & 0x40:
                        trest=trest+0.250
                    if lowValue & 0x20:
                        trest=trest+0.125
                    if lowValue & 0x10:
                        trest=trest+0.0625
                
                Temperature = '{:.4f}'.format(highValue+trest)
                return Temperature
            except:
                self.reportError("An error during DAQ from sensor!")
                return str(88.88)
        
    def setResolution(self, res):
        try:
            x = "{0:08b}".format(self.readCommandByte()) # Get Status-byte in binary form
            if res == "9":
                x = x[:4] + "00" + x[6:]
            elif res == "10":
                x = x[:4] + "01" + x[6:]
            elif res == "11":
                x = x[:4] + "10" + x[6:]
            elif res == "12":
                x = x[:4] + "11" + x[6:]
            else:
                self.reportError("Resolution '" + res + "' not supported!")
            x = int(x,2)
            self.writeCommandByte(x)
            self.reportMessage("Resolution set to '" + res + "'")
        except:
            self.reportError("Error occured during setting the resolution for sensor!")
        
    def writeCommandByte(self, byte):
        try:
            self.sens.write_byte_data(self.__address, 0xAC, byte)
            self.reportMessage("CMD byte set: " + "{0:08b}".format(byte))
        except:
            self.reportError("Error occured during writing of the command byte!")
                
    def readCommandByte(self):
        try:
            x = self.sens.read_byte_data(self.__address, 0xAC)
            self.reportMessage("CMD byte received: {0:08b}".format(x))
            return x
        except:
            self.reportError("Error occured during reading of the command byte!")
        
    def resetSensor(self):
        try:
            self.sens.write_byte(self.__address, 0x54)
            self.reportMessage("Sensor reset!")
        except:
            self.reportError("Error occured during reseting sensor!")
            
    def startTempMeasurement(self):
        try:
            self.sens.write_byte(self.__address, 0x51)
            self.reportMessage("Temperature measurement started.")
        except:
            self.reportError("Error occured starting temperature measurement!")
        
    def stopTempMeasurement(self):
        try:
            self.sens.write_byte(self.__address, 0x22)
            self.reportMessage("Temperature measurement stopped.")
        except:
            self.reportError("Error occured stopping temperature measurement!")
            
    def readTemp(self):
        try:
            print(self.get_temperature())
            self.reportMessage("Temperature measured.")
        except:
            self.reportError("Error occured while reading temperature!")
            
    def get_address(self):
        return self.__address

# ------------------------- End of Temp Sensor DS1631Z --------------------------

# ------------------------- Class Temp Sensor MAX31865 --------------------------
# Temperature sensor from Maxim Integrated
        
class Sensor_MAX31865(SensorTemp):
    def __init__(self, commServer, IF, name, model, simulationMode, tempRange, rRef, RTD, address):
        SensorTemp.__init__(self, commServer, IF, name, model, simulationMode, tempRange)      
        self.__byte = bytearray(1)
        self.__addr = address
        self.__rRef = int(rRef)
        self.__R0 = RTDtoR0(RTD)
        self.__setupSensor()
        
    def __setupSensor(self):
        self.__setRegVal(0,bytes((int('11000000',2),)))
    
    def connectToSensor(self):
        if self._simulationMode:
            return True
        else:
            return True
        
    def getValue(self):
        if self._simulationMode:
            self._simCount = self._simCount + self._simRate
            return '{:.2f}'.format(20*math.sin(math.pi*self._simCount))
        else:
            MSB = self.__getRegVal(1)
            LSB = self.__getRegVal(2)
            # print('{:02x}'.format(MSB) + ' | ' + '{:02x}'.format(LSB))
            return str(self.__convertRegToTemp(MSB,LSB))
            
    def __getRegVal(self,addr):
        self.__IF.activateIF(self.__addr)
        self.__IF.__write(bytes((int((self.__createOpcode(False) + '{:03b}'.format(addr)),2),)))
        self.__IF.__readInto(self.__byte)
        self.__IF.deactivateIF(self.__addr)
        #print('{:02x}'.format(self.getByte()))
        return(self.getByte())
        
    def __setRegVal(self,addr,val):
        self.__IF.activateIF(self.__addr)
        self.__IF.__write(bytes((int((self.__createOpcode(True) + '{:03b}'.format(addr)),2),)))
        self.__IF.__write(val)
        self.__IF.deactivateIF(self.__addr)
        
    def getByte(self):
        return self.__byte[0]
    
    def __convertRegToTemp(self, MSB,LSB):
        ADC = int('{:08b}'.format(MSB) + '{:08b}'.format(LSB)[:7],2)    # Calculate ADC-code
        RTD = ADC*self.__rRef/32768                                     # Calculate resistance of RTD
        T =  RtoT(self.__R0,RTD)                                        # Calculate Temperature
        return T
        
    @staticmethod
    def __createOpcode(Write):
        if Write==True:
            return '10000'
        else:
            return '00000'
    
# ------------------------- End of Temp Sensor MAX31865 --------------------------
            
def RTDtoR0(RTDtype):
    if RTDtype == 'PT100':
        return 100
    elif RTDtype == 'PT1000':
        return 1000
    else:
        return None

def RtoT(R0,R):
    a = 3.91E-3*R0
    b = -5.78E-7*R0
    T = (-a + math.sqrt(a*a-4*b*(R0-R)))/(2*b)
    return T