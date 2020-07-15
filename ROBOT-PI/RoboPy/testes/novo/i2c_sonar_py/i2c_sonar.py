#!/usr/bin/env python

# i2c_sonar.py
# 2016-03-24
# Public Domain

import time

import pigpio # http://abyz.co.uk/rpi/pigpio/python.html

class sensor:

   """
   A class to read up to 8 HC-SR04 acoustic rangers attached
   to a MCP23017 I2C port expander.

   Each ranger needs two GPIO, one for the echo pin and one for
   the trigger pin.

   The MPC23017 has 16 GPIO: 8 in port A and 8 in port B.

   Port A is configured as an input and should be connected
   to the ranger echo lines.  Port B is configured as an output
   and should be connected to the ranger trigger line.

   The rangers are referred to as ranger 0 to ranger 7.  Ranger x
   should be connected to pin Ax (echo) and pin Bx (trigger).

   Two modes of operation are supported - interrupt driven or not
   interrupt driven.  The interrupt driven mode is preferred but
   requires the use of one spare Pi GPIO.  This GPIO should be
   connected to pin 20 (INTA) of the MCP23017.

   The range is reported in cms.  An invalid reading is
   reported as 9999.
   """
   # To get fast sequential reads we use banked mode.  If banked
   # mode isn't used then only half the accuracy will be achieved.

   IOCON=10

   IOCON1=5
   IOCON2=21

   IODIRA=0
   IODIRB=16

   GPIOA=9
   GPIOB=25

   GPINTENA=2
   DEFVALA=3
   INTCONA=4

   BANK=(1<<7)
   SEQOP=(1<<5)
   INTPOL=(1<<1)

   MODE = BANK + SEQOP + INTPOL

   # You will need to change TRIGGER_GAP if you are using
   # interrupts and the value is incorrect for your ranger.

   TRIGGER_GAP=430 # Micros between trigger and echo going high.

   SPEED_OF_SOUND = 340.29 # metres per second

   MICS2CMS = SPEED_OF_SOUND / 20000.0 # Allowing for round trip

   INVALID_READING=9999.0

   def __init__(self, pi, addr=0x20, i2c_bus=1, INTA_GPIO=None,
                          i2c_kbps=100.0, max_range_cms=400):
      """
      Instantiate with the Pi and the I2C address of the
      MCP23017.

      Optionally the I2C bus may be specified (default 1).

      Optionally the GPIO connected to the interrupt line
      of the MCP23017 may be specified (default None).

      Optionally the I2C bus speed may be specified (default
      100 kbps).  You should specify this parameter if you
      are not using the standard I2C bus speed.

      Optionally the ranger maximum range in centimetres may
      be specified (default 400).
      """

      self.pi = pi
      self._cb = None
      self._INTA_GPIO = INTA_GPIO

      self._timeout = (2.0 * max_range_cms / 100.0) / sensor.SPEED_OF_SOUND

      if self._timeout < 0.001:
         self._timeout = 0.001
      elif self._timeout > 0.05:
         self._timeout = 0.05

      self._h = pi.i2c_open(i2c_bus, addr)

      # Check to see if already initialised.

      m1 = pi.i2c_read_byte_data(self._h, sensor.IOCON1)
      m2 = pi.i2c_read_byte_data(self._h, sensor.IOCON2)

      if (m1 != sensor.MODE) or (m2 != sensor.MODE):

         # Initialise to BANK + SEQOP
         pi.i2c_write_byte_data(self._h, sensor.IOCON, sensor.MODE)

      # Initialise A as inputs, B as outputs.

      # A is used for the echo lines.
      # B is used for the trigger lines.

      pi.i2c_write_byte_data(self._h, sensor.IODIRA, 0xFF) # A is inputs.
      pi.i2c_write_byte_data(self._h, sensor.IODIRB, 0x00) # B is outputs.

      self._bus_byte_micros = 1000000.0 / (i2c_kbps * 1000.0) * 9.0

      if INTA_GPIO is not None:

         pi.i2c_write_byte_data(self._h, sensor.GPINTENA, 0x00) # Disable.
         pi.i2c_write_byte_data(self._h, sensor.DEFVALA, 0x00)  # N/A.
         pi.i2c_write_byte_data(self._h, sensor.INTCONA, 0x00)  # On change.

         pi.set_mode(INTA_GPIO, pigpio.INPUT)

         self._cb = pi.callback(INTA_GPIO, pigpio.RISING_EDGE, self._cbf)

         self._tick = None
         self._edge = 3
         self._micros = 0
         self._reading = False

         self._trigger_gap = int(sensor.TRIGGER_GAP / self._bus_byte_micros)-1

      else:

         bytes = int(self._timeout * 1000000.0 / self._bus_byte_micros)
         self._bytes_lsb = bytes & 0xFF
         self._bytes_msb = (bytes>>8) & 0xFF

   def _cbf(self, gpio, level, tick):
      """
      Each edge of the echo pin creates an interrupt and thus a rising
      edge on the interrupt pin.
      """
      if self._edge == 1:
         self._tick = tick
      elif self._edge == 2:
         diff = pigpio.tickDiff(self._tick, tick)
         self._micros = diff
         self._reading = True
      self._edge += 1

   def read(self, ranger):
      """
      Triggers and returns a sonar ranger reading.  The reading is
      the number of centimetres to the detected object.

      ranger is 0 for the sensor connected to A0/B0, 1 for the sensor
      connected to A1/B1 etc.
      """
      if self._INTA_GPIO is not None:

         self._edge = 1
         self._reading = False

         count, data = self.pi.i2c_zip(self._h, 
            [7, 2, sensor.GPINTENA, 1<<ranger, # Interrupt on ranger.
             7, 1, sensor.GPIOA,               # Clear interrupts.
             6, 1,
             7, 3, sensor.GPIOB, 1<<ranger, 0, # Send trigger.
             7, 1, sensor.GPIOA,               # Consume interrupt.
             6, self._trigger_gap])

         timeout = time.time() + self._timeout
         while not self._reading:
            if time.time() > timeout:
               return sensor.INVALID_READING
            time.sleep(0.01)

         return self._micros * sensor.MICS2CMS

      else:

         # Send trigger on B then do multiple sequential reads of A.

         count, data = self.pi.i2c_zip(self._h, 
            [7, 3, sensor.GPIOB, 1<<ranger, 0,
             7, 1, sensor.GPIOA,
             1,
             6, self._bytes_lsb, self._bytes_msb])

         if (data[0] & (1<<ranger)) == 0: # Ignore data if trigger start missed.
            f = False
            for i in range(count):
               v = data[i] & (1<<ranger) # Mask off all but echo bit.
               if f:
                  if not v:
                     return i * self._bus_byte_micros * sensor.MICS2CMS
                     break
               else:
                  if v:
                     f = True
         return sensor.INVALID_READING

   def cancel(self):
      """
      Cancels the sonar rangers and releases resources.
      """
      self.pi.i2c_close(self._h)
      if self._cb is not None:
         self._cb.cancel()

if __name__ == "__main__":

   import time

   import pigpio
   import i2c_sonar

   TIME=60.0

   pi=pigpio.pi() # Connect to local Pi.

   if not pi.connected:
      exit(0)

   s = i2c_sonar.sensor(pi, addr=0x27, INTA_GPIO=None, max_range_cms=200)

   stop = time.time() + TIME

   while time.time() < stop:
      v = s.read(0) # 0 is ranger 0 (connected to A0/B0).
      r = round(v,1)
      print(r)
      time.sleep(0.1)

   s.cancel()

   pi.stop()

