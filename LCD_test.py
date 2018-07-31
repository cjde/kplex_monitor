import time
import smbus

BUS = 1
ADDRESS = 0x38
Device_addr = [0,0,0]
Device_ctrl = [0,0,0]
Segment_addr = [ 0x04, 0x05, 0x06, 0x07, 0x08 ] 

# ========== Control Register 0 ===========

# Bits 3:2  frame frequency selection
#		00 ffr32Hz
ffr32Hz = 0b00000000

#		01 ffr64Hz
ffr64Hz = 0b00000100

#		10 ffr96Hz
ffr96Hz = 0b00001000

#		11 ffr128Hz
ffr128Hz = 0b00001100

# Bits 1:1
#			0  IntOscEnable
IntOscEnable = 0b00000000
#			1  IntOscDisable
IntOscDisable = 0b00000010

# Bits 0:0
#			 1  ClkOutEnable
ClkOutEnable = 0b00000001
#			 0  ClkOutDisable
ClkOutDisable = 0b00000000

# default value
Device_addr[0] = 0x01
Device_ctrl[0] = ffr64Hz | IntOscEnable | ClkOutDisable

# ========== Control Register 1 ===========

# 4:4 BOOST large display mode support
# 0 standard power drive scheme
Boostoff = 0b00010000
# 1 enhanced power drive scheme for higher display loads
BoostOn = 0b00010000

# 3:2 multiplex drive mode selection
# 00 multiplex drive mode; COM0 to COM3 (nMUX = 4)
Nmux4 = 0b00000000
# 01 multiplex drive mode; COM0 to COM2 (nMUX = 3)
Nmux3 = 0b00000100
# 10 multiplex drive mode; COM0 and COM1 (nMUX = 2)
Nmux2 = 0b00001000
# 11 static drive mode; COM0 (nMUX = 1)
Nmux1 = 0b00001100

# 0 1/3 bias (abias = 2)

# 1:1 bias mode selection
Bias2 = 0b00000000
# 1 1/2 bias (abias = 1)
Bias1 = 0b00000010

# 0:0 DE display enable[3]
# 0 display disabled; device is in power-down mode
DisplayOn = 0b00000001
# 1 display enabled; device is in power-on mode
DisplayOff = 0b00000000
Device_addr[1] = 0x02
Device_ctrl[1] = BoostOn | Nmux1 | Bias2 | DisplayOn

# ========== Control Register 2 ===========
# 2:1 blink control
# 00[1] blinking off
BlinkOff = 0b00000000
# 01 blinking on, fblink = 0.5 Hz
Blink05 = 0b00000010
# 10 blinking on, fblink = 1 Hz
Blink1 = 0b00000100
# 11 blinking on, fblink = 2 Hz
Blink2 = 0b00000110

# 0:0 INV inversion mode selection
# 0[ line inversion (driving scheme A)
LineInv = 0b00000000
# 1 frame inversion (driving scheme B)
FrameInv = 0b00000001
Device_addr[2] = 0x03
Device_ctrl[2] = Blink05 | LineInv


bus = smbus.SMBus(BUS)

for dev in range(0,3):
   print "Device Ctrl ",dev 
   config = bus.read_byte_data(ADDRESS, Device_addr[dev])
   print "	current state: ",config," new state: ",Device_ctrl[dev]
   bus.write_byte_data(ADDRESS, Device_addr[dev], Device_ctrl[dev])
   config = bus.read_byte_data(ADDRESS, Device_addr[dev])
   print "	state set to :", config

print ""
print "turning ON all bits" 
allseg = 0b11111111

for reg in Segment_addr: 
    bus.write_byte_data(ADDRESS, reg, allseg)
    config = bus.read_byte_data(ADDRESS, reg)
    print "      segments set to :", config

time.sleep(300)

print "turning OFF all bits" 
allseg = 0b00000000

for reg in Segment_addr:
    bus.write_byte_data(ADDRESS, reg, allseg)
    config = bus.read_byte_data(ADDRESS, reg)
    print "      segments set to :", config

print "turning OFF Display " 
Device_ctrl[1] = Boostoff | Nmux4 | Bias2 | DisplayOff
bus.write_byte_data(ADDRESS, Device_addr[1], Device_ctrl[1])


