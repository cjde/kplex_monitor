# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import time

from Adafruit_LED_Backpack import SevenSegment

display = [0,0,0]


# Create display instance on default I2C address (0x70) and bus number.
#display[0] = SevenSegment.SevenSegment()

# Alternatively, create a display with a specific I2C address and/or bus.
display[0] = SevenSegment.SevenSegment(address=0x70, busnum=1)

# Initialize the display. Must be called once before using the display.
display[0].begin()

# Keep track of the colon being turned on or off.
colon = False

# Run through different number printing examples.
print('Press Ctrl-C to quit.')
numbers = [270, 271, 275, 280, 275, 270, 280, 281, 180, 188, 190,195,194 ]
while True:
    # Print the same numbers with no decimal digits and left justified.
    for i in numbers:
        display[0].clear()
        display[0].print_float(i, decimal_digits=0, justify_right=True)
        display[0].set_colon(colon)
        display[0].write_display()
        time.sleep(1.0)
