import math, time

VERBOSE = 1             # Set Behavior or console-output (0: No messages; 1: Only important; 3: All messages)
Refresh = 1000
IP = ''
timeStart = 0
timeElapsed = 0

def printMsg(text, lvl=None):
    if lvl == None:
        lvl = 1
    if lvl <= VERBOSE:
        print("Debug:--- ", text)
        
def printTime(msg):
    global timeElapsed
    timeDiff = getTime()
    timePassed = timeDiff - timeElapsed
    timeElapsed += timePassed
    print('Timing:--- ' + str(timeDiff) + ' ms; ' + ' Since last tick: ' + str(timePassed) + ' ms; ' + msg)
    
def getTime():
    timeDiff = time.ticks_diff(time.ticks_ms(),timeStart)
    return timeDiff
    
def resetTime():
    global timeStart
    global timeElapsed
    timeStart = time.ticks_ms()
    timeElapsed = 0 
    
def getRefreshRate():
    return Refresh

def getIPAddress():
    return IP
            
def setVerboseLvl(lvl):
    global VERBOSE
    VERBOSE = lvl
    
def setRefreshRate(rate):
    global Refresh
    Refresh = rate
    
def setIPAddress(ip):
    global IP
    IP = ip
            
def getBool(boolString):
    if boolString == "TRUE":
        return True
    elif boolString == "True":
        return True
    elif boolString == "FALSE":
        return False
    else:
        return False
    
def toggle(p):
    p.value(not p.value())