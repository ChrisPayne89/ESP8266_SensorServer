import supp

class CMDMngr:
    def __init__(self,commServer,IFMngr,SensMngr):
        self.__commServer = commServer    
        self.__IFMngr = IFMngr
        self.__SensMngr = SensMngr
        
    def resolveCMD(self,CMD, para):
        try:
            if CMD == "Test":
                self.__commServer.sendMessage("Resolved CMD 'Test'", 2)
            elif CMD == "SensorAdd":
                self.__commServer.sendMessage("Resolved CMD 'SensorAdd'", 2)
                self.__SensMngr.sensorAdd(para)
            elif CMD == "SensorRemove":
                self.__commServer.sendMessage("Resolved CMD 'SensorRemove'", 2)
                self.__SensMngr.sensorRemove(para)
            elif CMD == "SetRefreshRate":
                self.__commServer.sendMessage("Resolved CMD 'SetRefreshRate'", 2)
                try:
                    rate = int(para)
                    if rate > 0:
                        supp.setRefreshRate(rate)
                        self.__commServer.sendMessage("DAQ rate set to " + str(rate) + " ms", 1)
                    else:
                        self.__commServer.sendMessage("DAQ rate has to be greater than 0!", 1)
                except:
                    self.__commServer.sendError("An error occured while setting the refresh rate!")
            elif CMD == "SetSimulationMode":
                self.__commServer.sendMessage("Resolved CMD 'SetSimulationMode'", 2)
                sensData = para.split(";")
                sensName = sensData[0]
                sensMode = supp.getBool(sensData[1])
                self.__SensMngr.setSimulationMode(sensName,sensMode)
            elif CMD == "SetSimulationRate":
                self.__commServer.sendMessage("Resolved CMD 'SetSimulationRate",2)
                sensData = para.split(";")
                sensName = sensData[0]
                sensRate = float(sensData[1])
                self.__SensMngr.setSimulationRate(sensName,sensRate)
            elif CMD == "ResetSimulation":
                self.__commServer.sendMessage("Resolved CMD 'ResetSimulation",2)
                sensName = para
                self.__SensMngr.resetSimulation(sensName)
            elif CMD == "SetResolution":
                self.__commServer.sendMessage("Resolved CMD 'SetResolution'", 2)
                sensData = para.split(";")
                sensName = sensData[0]
                sensRes = sensData[1]
                self.__SensMngr.setResolution(sensRes)
            elif CMD == "GetCMDByte":
                self.__commServer.sendMessage("Resolved CMD 'GetCMDByte'", 2)
                self.__SensMngr.getCMDByte(para)
            elif CMD == "ResetSensor":
                self.__commServer.sendMessage("Resolved CMD 'ResetSensor'", 2)
                self.__SensMngr.resetSensor(para)
            elif CMD == "StartTemp":
                self.__commServer.sendMessage("Resolved CMD 'StartTemp'", 2)
                self.__SensMngr.startTempMeasurement(para)
            elif CMD == "StopTemp":
                self.__commServer.sendMessage("Resolved CMD 'StopTemp'", 2)
                self.__SensMngr.stopTempMeasurement(para)
            elif CMD == "ReadTemp":
                self.__commServer.sendMessage("Resolved CMD 'ReadTemp'", 2)
                self.__SensMngr.readTemp(para)
            elif CMD == "StatusNetstat":
                self.__commServer.sendMessage("Resolved CMD 'netstat'", 2)
                conns, bytesRcvr = self.__commServer.getCountRcvr()
                self.__commServer.sendCMD("StatusNetstat", supp.getIPAddress() + ";" + str(conns) + ";" + str(bytesRcvr))
            elif CMD == "StatusPing":
                self.__commServer.sendMessage("Resolved CMD 'StatusPing'", 2)
                self.__commServer.sendCMD("StatusPing", supp.getIPAddress() + ";" + para)
            elif CMD == "SetVerboseLvl":
                self.__commServer.sendMessage("Resolved CMD 'SetVerboseLvl'", 2)
                self.__commServer.setVerboseLvl(int(para))
                supp.setVerboseLvl(int(para))
            else:
                self.__commServer.sendError("Received unknown CMD!")
        except:
            self.__commServer.sendError("Error while resolving CMD!")