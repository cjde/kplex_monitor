from __future__ import print_function
import time
import smbus

BUS = 1
ADDRESS = 0x38
Device_addr = [0,0,0]
Device_ctrl = [0,0,0]
Digit = [ 0,1,2,3,4,5,6,7,8,9 ]
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
Device_ctrl[1] = Boostoff | Nmux2 | Bias2 | DisplayOn

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
Device_ctrl[2] = BlinkOff | LineInv

# Digit to segment mapping 
'''
--A--
|   |
F   B
|   |
--G--
|   |
E   C
|   |
--D-- 
'''

A = 0b00000001
B = 0b00000010
C = 0b00000100
D = 0b00001000
E = 0b00010000
F = 0b00100000
G = 0b01000000

Digit[0]  = A|B|C|D|E|F 
Digit[1]  =   B|C
Digit[2]  = A|B|  D|E  |G 
Digit[3]  = A|B|C|D    |G 
Digit[4]  =   B|C    |F|G 
Digit[5]  = A  |C|D  |F|G 
Digit[6]  = A  |C|D|E|F|G 
Digit[7]  = A|B|C         
Digit[8]  = A|B|C|D|E|F|G 
Digit[9]  = A|B|C|D  |F|G 
blank     = 0x00

bus = smbus.SMBus(BUS)

for dev in range(0,3):
   print( "Device Ctrl ",dev )
   config = bus.read_byte_data(ADDRESS, Device_addr[dev])
   print ("	current state: ",config," new state: ",Device_ctrl[dev])
   bus.write_byte_data(ADDRESS, Device_addr[dev], Device_ctrl[dev])
   config = bus.read_byte_data(ADDRESS, Device_addr[dev])
   print ( "	state set to :", config ) 

# turn on one segment and a time and record which bit turns on which segment 
# the LCD is layed out so that the pins can easiley be soldered to the LCD driver carrier 
# in that pins 32-48 connect to the same side of the LCD pins 5-20    
   

#for reg in range(4,8):
#    bus.write_byte_data(ADDRESS, reg, Digit[0])

for d1 in range(0,10):  
    bus.write_byte_data(ADDRESS, Segment_addr[3], Digit[d1])
    print(d1,",",end="") 
    for d2 in range(0,10):  
        print(d2,end="") 
        bus.write_byte_data(ADDRESS, Segment_addr[2], Digit[d2])
        for d3 in range(0,10):  
            print(d3,end="") 
            bus.write_byte_data(ADDRESS, Segment_addr[1], Digit[d3])
            for d4 in range(0,10):  
#                print(d4,end="") 
                try:
                   bus.write_byte_data(ADDRESS, Segment_addr[0], Digit[d4])
                except: 
                     print(" caught bus error ")
                time.sleep(.01)
        print("")


		
		
print ( "turning OFF all bits" )
allseg = 0b00000000

for reg in Segment_addr:
    bus.write_byte_data(ADDRESS, reg, allseg)
    config = bus.read_byte_data(ADDRESS, reg)
    print ("      segments set to :", config)

print ( "turning OFF Display ")
Device_ctrl[1] = Boostoff | Nmux4 | Bias2 | DisplayOff
bus.write_byte_data(ADDRESS, Device_addr[1], Device_ctrl[1])



