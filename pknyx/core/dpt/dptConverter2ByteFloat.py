# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pknyx.org}) is Copyright:
  - (C) 2013 Frédéric Mantegazza

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
or see:

 - U{http://www.gnu.org/licenses/gpl.html}

Module purpose
==============

Datapoint Types management

Implements
==========

 - B{DPTConverter2ByteFloat}

Usage
=====

see L{DPTConverterBoolean}

@todo: handle NaN

@author: Frédéric Mantegazza
@copyright: (C) 2013 Frédéric Mantegazza
@license: GPL
"""

__revision__ = "$Id$"

import struct

from pknyx.common.loggingServices import Logger
from pknyx.core.dpt.dptId import DPTID
from pknyx.core.dpt.dpt import DPT
from pknyx.core.dpt.dptConverterBase import DPTConverterBase, DPTConverterValueError


class DPTConverter2ByteFloat(DPTConverterBase):
    """ DPT converter class for 2-Byte-Float (F16) KNX Datapoint Type

    G{classtree}

     - 2 Byte Float: SEEEEMMM MMMMMMMM
     - S: Sign [0, 1]
     - E: Exponent [0:15]
     - M: Significand (Mantissa) [-2048:2047]

    For all Datapoint Types 9.xxx, the encoded value 7FFFh shall always be used to denote invalid data.
    """
    DPT_Generic = DPT("9.xxx", "Generic", (-670760.96, +670760.96))

    DPT_Value_Temp = DPT("9.001", "Temperature", (-273, +670760), "°C")
    DPT_Value_Tempd = DPT("9.002", "Temperature difference", (-670760, +670760), "K")
    DPT_Value_Tempa = DPT("9.003", "Temperature gradient", (-670760, +670760), "K/h")
    DPT_Value_Lux = DPT("9.004", "Luminous emittance", (0, +670760), "lx")
    DPT_Value_Wsp = DPT("9.005", "Wind speed", (0, +670760), "m/s")
    DPT_Value_Pres = DPT("9.006", "Air pressure", (0, +670760), "Pa")
    DPT_Value_Humidity = DPT("9.007", "Humidity", (0, +670760), "%")
    DPT_Value_AirQuality = DPT("9.008", "Air quality", (0, +670760), "ppm")
    DPT_Value_Time1 = DPT("9.010", "Time difference 1", (-670760, +670760), "s")
    DPT_Value_Time2 = DPT("9.011", "Time difference 2", (-670760, +670760), "ms")
    DPT_Value_Volt = DPT("9.020", "Electrical voltage", (-670760, +670760), "mV")
    DPT_Value_Current = DPT("9.021", "Electric current", (-670760, +670760), "mA")
    DPT_PowerDensity = DPT("9.022", "Power density", (-670760, +670760), "W/m²")
    DPT_KelvinPerPercent = DPT("9.023", "Kelvin/percent", (-670760, +670760), "K/%")
    DPT_Power = DPT("9.024", "Power", (-670760, +670760), "kW")
    DPT_Value_Volume_Flow = DPT("9.025", "Volume flow", (-670760, 670760), "l/h")
    DPT_Rain_Amount = DPT("9.026", "Rain amount", (-670760, 670760), "l/m²")
    DPT_Value_Temp_F = DPT("9.027", "Temperature (°F)", (-459.6, 670760), "°F")
    DPT_Value_Wsp_kmh = DPT("9.028", "Wind speed (km/h)", (0, 670760), "km/h")

    def _checkData(self, data):
        if not 0x0000 <= data <= 0xffff:
            raise DPTConverterValueError("data %s not in (0x0000, 0xffff)" % hex(data))

    def _checkValue(self, value):
        if not self._dpt.limits[0] <= value <= self._dpt.limits[1]:
            raise DPTConverterValueError("Value not in range %r" % repr(self._dpt.limits))

    def _toValue(self):
        sign = (self._data & 0x8000) >> 15
        exp = (self._data & 0x7800) >> 11
        mant = self._data & 0x07ff
        if sign <> 0:
            mant = -(~(mant - 1) & 0x07ff)
        value = (1 << exp) * 0.01 * mant
        #Logger().debug("DPTConverter2ByteFloat.dataToValue(): sign=%d, exp=%d, mant=%r" % (sign, exp, mant))
        #Logger().debug("DPTConverter2ByteFloat.dataToValue(): value=%.2f" % value)
        return value

    def _fromValue(self, value):
        sign = 0
        exp = 0
        if value < 0:
            sign = 1
        mant = int(value * 100)
        while not -2048 <= mant <= 2047:
            mant = mant >> 1
            exp += 1
        #Logger().debug("DPTConverter2ByteFloat._fromValue(): sign=%d, exp=%d, mant=%r" % (sign, exp, mant))
        data = (sign << 15) | (exp << 11) | (int(mant) & 0x07ff)
        #Logger().debug("DPTConverter2ByteFloat._fromValue(): data=%s" % hex(data))
        self._data = data

    def _toStrValue(self):
        s = "%.2f" % self.value

        # Add unit
        if self._displayUnit and self._dpt.unit is not None:
            try:
                s = "%s %s" % (s, self._dpt.unit)
            except TypeError:
                Logger().exception("DPTConverter2ByteFloat._toStrValue()", debug=True)
        return s

    #def _fromStrValue(self, strValue):

    def _toFrame(self):
        return struct.pack(">H", self._data)

    def _fromFrame(self, frame):
        self._data = struct.unpack(">H", frame)[0]


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')

    class DPTConverter2ByteFloatTestCase(unittest.TestCase):

        def setUp(self):
            self.testTable = (
                (     0.,   0x0000, "\x00\x00"),
                (     0.01, 0x0001, "\x00\x01"),
                (    -0.01, 0x87ff, "\x87\xff"),
                (    -1.,   0x879c, "\x87\x9c"),
                (     1.,   0x0064, "\x00\x64"),
                (  -272.96, 0xa156, "\xa1\x56"),
                (670760.96, 0x7fff, "\x7f\xff"),
            )
            self.conv = DPTConverter2ByteFloat("9.xxx")

        def tearDown(self):
            pass

        #def test_constructor(self):
            #print self.conv.handledDPTIDs

        def test_checkValue(self):
            with self.assertRaises(DPTConverterValueError):
                self.conv._checkValue(self.conv._dpt.limits[1] + 1)

        def test_toValue(self):
            for value, data, frame in self.testTable:
                self.conv.data = data
                value_ = self.conv.value
                self.assertEqual(value_, value, "Conversion failed (converted value for %s is %.2f, should be %.2f)" %
                                 (hex(data), value_, value))

        def test_fromValue(self):
            for value, data, frame in self.testTable:
                self.conv.value = value
                data_ = self.conv.data
                self.assertEqual(data_, data, "Conversion failed (converted data for %.2f is %s, should be %s)" %
                                 (value, hex(data_), hex(data)))

        def test_toFrame(self):
            for value, data, frame in self.testTable:
                self.conv.data = data
                frame_ = self.conv.frame
                self.assertEqual(frame_, frame, "Conversion failed (converted frame for %s is %r, should be %r)" %
                                 (hex(data), frame_, frame))

        def test_fromFrame(self):
            for value, data, frame in self.testTable:
                self.conv.frame = frame
                data_ = self.conv.data
                self.assertEqual(data_, data, "Conversion failed (converted data for %r is %s, should be %s)" %
                                 (frame, hex(data_), hex(data)))

    unittest.main()
