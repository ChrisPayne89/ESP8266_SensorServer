# This file is executed on every boot (including wake-boot from deepsleep)
import esp
esp.osdebug(None)
import gc
import network
import machine
import time
#import webrepl
#webrepl.start()
gc.collect()

# Try to connect to the local network, activate Station interface if deactiva
sta = network.WLAN(network.STA_IF)
if sta.active() == 0:
    ap = network.WLAN(network.AP_IF)
    ap.active(0)
    sta.active(1)

if machine.reset_cause() != machine.SOFT_RESET:
    # Configure static IP of the module, must match the address space of the router
    #sta.ifconfig(('192.168.2.3','255.255.255.0','0.0.0.0','0.0.0.0'))
    sta.ifconfig(('192.168.238.3','255.255.255.0','0.0.0.0','0.0.0.0'))

if not sta.isconnected():
    #sta.connect('PCSputterDAQ','Spu77ern')
    sta.connect('Connectify-VIPER','gimme595')
    while not sta.isconnected():
        time.sleep_ms(1000)