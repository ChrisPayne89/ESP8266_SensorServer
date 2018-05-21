import machine

# ------------------------- Class IFMngr --------------------------

class IFMngr:
    def __init__(self,commServer):
        self.__commServer = commServer
        self.__IFs = []
 
    def addIF(self,IFType,name,**kwargs):
        for iface in self.__IFs:
            if name == iface.getName():
                raise Exception('IF already defined!')
        if IFType == 'SPI':
            self.__IFs.append(IFSpi(name,kwargs['sck'],kwargs['mosi'],kwargs['miso'],kwargs['cs']))
        if IFType == 'SPIMux':
            self.__IFs.append(IFSpiMux(name,kwargs['spi'],kwargs['muxLst']))
        if IFType == 'I2C':
            self.__IFs.append(IFI2C(name))
    
    def getIF(self,name):
        for IF in self.__IFs:
            if name == IF.getName():
                return IF
     
# ------------------------- End of IFMngr --------------------------
                
# ------------------------- Class IF --------------------------
                
class IF:
    def __init__(self,name):
        self.__name = name
        
    def getName(self):
        return self.__name
    
    def setAddress(self,addr):
        pass
    
# ------------------------- End of IF --------------------------

# ------------------------- Class IFSpi --------------------------
        
class IFSpi(IF):
    def __init__(self,name,sck,mosi,miso,cs):
        IF.__init__(self,name)
        self.__cs = None
        self.__spi = None
        self._iniCs(cs)
        self._iniSpi(sck,mosi,miso)
    
    def _iniCs(self,pin):
        self.__cs = machine.Pin(pin,machine.Pin.OUT)
        
    def _iniSpi(self,sck,mosi,miso):
        sck = machine.Pin(sck,machine.Pin.OUT)
        mosi = machine.Pin(mosi,machine.Pin.OUT)
        miso = machine.Pin(miso,machine.Pin.IN)
        self.__spi = machine.SPI(-1,sck=sck,mosi=mosi,miso=miso)
        self.__spi.deinit()
        self.__spi.init(baudrate=500000,polarity=1,phase=1)
            
    def writeBytes(self,byteList):
        self.__cs.off()
        for byte in byteList:
            self.__spi.write(byte)
        self.__cs.on()
        
    def __csHigh(self):
        self.__cs.on()
        
    def __csLow(self):
        self.__cs.off()
        
    def __write(self,byte):
        self.__spi.write(byte)
    
    def __readInto(self,buf):
        self.__spi.readinto(buf)
        
# ------------------------- End of IFSpi --------------------------

# ------------------------- Class IFSpiMux --------------------------

class IFSpiMux(IF):
    def __init__(self,name,spi,muxs):
        IF.__init__(self,name)
        self.__spi = spi
        self.__muxs = muxs
    
    def addMux(self,mux):
        self.__muxs.append(mux)
    
    def setAddress(self,addr):
        addrrslv = addr.split('::')
        for mux in self.__muxs:
            mux.closeConns()
        for mux in self.__muxs:
            if mux.getAddr()==int(addrrslv[0]):
                mux.openConn(int(addrrslv[1]))
                
    def writeBytes(self,byteList):
        self.__spi.__csLow()
        for byte in byteList:
            self.__spi.__write(byte)
        self.__spi.__csHigh()
    
    def activateIF(self,addr):
        addrrslv = addr.split('::')
        for mux in self.__muxs:
            if mux.getAddr()==int(addrrslv[0]):
                mux.openConn(int(addrrslv[1]))
                
    def deactivateIF(self,addr):
        for mux in self.__muxs:
            mux.closeConns()
            
    def __csHigh(self):
        self.__spi.__csHigh()
        
    def __csLow(self):
        self.__spi.__csLow()
        
    def __write(self,byte):
        self.__spi.__write(byte)
    
    def __readInto(self,buf):
        self.__spi.__readInto(buf)

# ------------------------- End of IFSpiMux --------------------------
        
# ------------------------- Class IFI2C --------------------------
        
class IFI2C(IF):
    def __init__(self,name):
        IF.__init__(self,name)
        
# ------------------------- End of IFI2C --------------------------

# ------------------------- Class Mux --------------------------

class Mux():
    def __init__(self,IF,addr):
        self.__IF = IF
        self.__addr = addr
    
    def openConn(self,addr):
        pass
    
    def closeConns(self):
        pass
     
    def getAddr(self):
        return self.__addr

# ------------------------- End of Mux --------------------------

# ------------------------- Class MCP23S17 --------------------------

class MCP23S17(Mux):
    def __init__(self,IF,addr):
        Mux.__init__(self,IF,addr)
        self.__byte = bytearray(1)
    
    def openConn(self,addr):
        addr=7-addr
        addrByte = '11111111'
        addrByte = addrByte[:addr]+'0'+addrByte[(addr+1):]
        addr = bytes((int(addrByte,2),))
        self.__setRegVal(b'\x00',addr)
    
    def closeConns(self):
        self.__setRegVal(b'\x00',b'\xff')
    
    def __getRegVal(self,reg):
        self.__IF.__csLow()
        self.__IF.__write(self.__createOpcode(False))
        self.__IF.__write(reg)
        self.__IF.__readInto(self.__byte)
        self.__IF.__csHigh()
        #print('{:02x}'.format(self.getByte()))
        
    def __setRegVal(self,reg,val):
        self.__IF.writeBytes((self.__createOpcode(True),reg,val))
        
    def __createOpcode(self,Write):
        op = '{:03b}'.format(self.__addr)
        if Write == True:
            op = op + '0'
        else:
            op = op + '1'
        op = '0100' + op
        op = bytes((int(op,2),))
        return op
        
    def getByte(self):
        return self.__byte[0]
    
# ------------------------- End of MCP23S17 --------------------------