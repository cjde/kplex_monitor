# kplex_monitor
Listens to kplex server and manipulates compass telemetry 

Kplex is NMEA mux that can receive NMEA data from several inputs. This program connects to kplex and listens for compass sentences, computes average track and displays heading and track on a seven segment I2C Adafruit LED display. It runs on a Rasberry PI Zero. The SDC and SDL pins are used for the display at address 70 (primary displau) and 71 The Adafruit I2C backpack is powered directly from an attached the 5V USB connector because of power requirements (the PI cant drive that current load). GPIO pins 32,36,38,40 are attached to LEDS that will illuminate when a 'gps', 'compass', 'speed', or 'unknown'  NMEA sentence is recieved from KPLEX.
