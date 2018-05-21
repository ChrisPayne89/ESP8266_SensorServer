import socket,time,supp

# ------------------------- class CommServer -------------------------
# Class that provides an interface for TCP/IP-communication with the host
            
class CommServer():
    def __init__(self,port,name,verbose):
        self.__conns = []
        self.__name = name
        self.__verbose = verbose
        self.__sock = None
        self.__initSocket(port)
        
    def __initSocket(self,port):
            addr = socket.getaddrinfo('0.0.0.0', port)[0][-1] 
            self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.__sock.bind(addr)
            self.__sock.listen(3)
            self.__sock.settimeout(0)
            supp.printMsg("Listening on " + str(addr) + ' ...', 1)
            
    def listenForClients(self,timeout):
        try:
            s, addr = self.__sock.accept()
            #s.settimeout(0)
            self.__addConn(Conn(s,addr))
            supp.printMsg("Client connected from " + str(addr),1)
            self.sendCMD("RegisterIP",supp.getIPAddress() + ";" + self.__name)
            return True
        except:
            supp.printMsg("Listening for Clients timed out", 1)
            return False
            pass
        
    def connectToHost(self,IP_addr,IP_port,Timeout):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        supp.printMsg("Connecting to host ...", 1)
        timeTot = 0
        while ((timeTot<Timeout)or(Timeout==-1))and(not self.__isConnected):
            try:
                s.connect((IP_addr, IP_port))
                s.settimeout(0.1)
                self.__addConn(Conn(s))
                self.sendMessage("Connection to Host established")
                self.sendCMD("RegisterIP","Wifi" ";" + self.__name)
            except:
                supp.printMsg("Connection attempt to Host failed. Elapsed time: " + str(timeTot/1000) + ' s', 1)
            time.sleep_ms(500)
            timeTot+=1000
        if timeTot>=Timeout:
            supp.printMsg("Connection to {0}{1} failed".format(IP_addr, IP_port),1)
        
    def __addConn(self,conn):
        self.__conns.append(conn)
        
    def readCMD(self):
        CMDs = []
        for conn in self.__conns:
            try:
                CMDs.append(conn.readCMD())
            except:
                pass
        return CMDs
    
    def sendMessage(self,text,lvl=None):
        if lvl == None:
            lvl = 1
        if lvl <= self.__verbose:
            print("Message:--- ",text)
            self.sendCMD("MESSAGE", self.__name + ";" + text)
            
    def sendError(self,text):
        print("Error:--- ", text)
        self.sendCMD("ERROR", self.__name + ";" + text)
            
    def sendCMD(self,cmd,para=None):
        for conn in self.__conns:
            conn.__sendData(self.buildCMD(cmd,para))
            
    def getCountRcvr(self):
        countRcvr = 0
        for conn in self.__conns:
            countRcvr = countRcvr + conn.getCountRcvr()
        return len(self.__conns), countRcvr
            
    def setVerboseLvl(self,lvl):
        if lvl >= 0 and lvl <= 3:
            self.__verbose = lvl
            self.sendMessage("Verbose level set to " + str(lvl), 1)
        else:
            self.sendError("The verbose level has to be in the range of (0..3)!", 1)
            
    @staticmethod
    def buildCMD(cmd,para=None):
        if para is None:
            cmdConc="{0:02d}".format(len(cmd)) + "{0:04d}".format(0) + cmd
            supp.printMsg("{0:02d}".format(len(cmd)) + "|" + "{0:04d}".format(0) + "|" + cmd, 3)
        else:
            cmdConc="{0:02d}".format(len(cmd)) + "{0:04d}".format(len(para)) + cmd + para
            supp.printMsg("{0:02d}".format(len(cmd)) + "|" + "{0:04d}".format(len(para)) + "|" + cmd + "|" + para, 3)
        return cmdConc          
            
# ------------------------- End of MsgServer --------------------------            

# ------------------------- class Conn -------------------------
# This connection class handles a connection to a host machine (through one specific port of the client)

class Conn():
    def __init__(self,socket,addr):
        self.__sock = socket
        self.remoteAddr = addr
        self.__recv = None
        self.__isConnected = True
        self.__countRecv = 0
        self.__initConn()
        
    def __initConn(self,):
        self.__recv = Receiver(self.__sock)
        
    def readCMD(self):
        try:
            CMD, Para, count = self.__recv.readServerData()
            self.__countRecv = self.__countRecv + count
            return CMD, Para
        except:
            supp.printMsg("Exception in Receiver " + str(self.remoteAddr), 3)
            pass
    
    def getCountRcvr(self):
        return self.__countRecv
            
    def __sendData(self,data):
        try:
            self.__sock.sendall(data.encode())
        except Exception as e:
            supp.printMsg("Exception in sendData()" + str(e), 1)
            #self.__closeConnection()
                  
    def __closeConnection(self):
        supp.printMsg("Closing socket")
        self.__sock.close()
        self.__isConnected = False 
        
    def isConnected(self):
        return self.__isConnected
    
# ------------------------- End of Conn -------------------------- 

# ------------------------- class Receiver -------------------------
# Create a new instance of this class to listen for incoming commands from a remote client

class Receiver():
    sizeAddrCMD = 2
    sizeAddrData = 4
    sizeCMD = 0
    sizeData = 0
    
    def __init__(self,sock):
        self.__sock = sock
        self.__countRecv = 0

    def readServerData(self):
        supp.printMsg("Reading socket", 2)
        blkAddrCMD = ""
        blkAddrData = ""
        blkCMD = ""
        blkData = ""
        try:
            supp.printMsg("Begin fetching data from socket buffer", 2)
            blkAddrCMD = self.__sock.recv(Receiver.sizeAddrCMD)
            sizeCMD = int(blkAddrCMD)
            if blkAddrCMD != None:
                try:
                    blkAddrData = self.__sock.recv(Receiver.sizeAddrData)
                    sizeData = int(blkAddrData)
                    try:
                        blkCMD = self.__sock.recv(sizeCMD)
                        blkData = self.__sock.recv(sizeData)
                        supp.printMsg("Received CMD block from server:\n"
                              "Data: " + str(len(blkCMD)) + " | " + str(blkCMD.decode("utf-8")) + "\n"
                              "Parameter: " + str(len(blkData)) + " | " + str(blkData.decode("utf-8")), 3)
                        count = Receiver.sizeAddrCMD + Receiver.sizeAddrData + sizeCMD + sizeData
                        return (str(blkCMD.decode("utf-8")), str(blkData.decode("utf-8")), count)
                    except:
                        supp.printMsg("Data block not recovered successfully", 1)
                        raise Exception("Data block not recovered successfully")
                except:
                    supp.printMsg("Parameter Address block not recovered successfully", 1)
                    raise Exception("Parameter Address block not recovered successfully")
            else:
                supp.printMsg("sock.recv() returned with None", 1)
                return ""
        except:
            supp.printMsg("Error during fetching data from socket buffer, most likely due to socket timeout", 3)
            pass
            
    def get_countRecv(self):
        return self.__countRecv

# ------------------------- End of Receiver -------------------------- 