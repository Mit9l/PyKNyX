# -*- coding: utf-8 -*-

""" Python KNX framework

License
=======

 - B{pKNyX} (U{http://www.pyknyx.org}) is Copyright:
  - (C) 2013-2015 Frédéric Mantegazza

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

Application layer group data management

Implements
==========

 - B{APDU}
 - B{APDUValueError}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""


from pyknyx.common.exception import PKNyXValueError
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.stack.layer7.apci import APCI


class APDUValueError(PKNyXValueError):
    """
    """


class APDU(object):
    """ APDU class
    """
    @classmethod
    def makeGroupValue(cls, apci, data=b"\x00", size=0):
        """ Create an APDU from apci and data

        @param apci: L{APCI}
        @type apci: int

        @param size: size of the data
        @type size: int
        """
        data = bytearray(data)

        if apci not in (APCI.GROUPVALUE_READ, APCI.GROUPVALUE_RES, APCI.GROUPVALUE_WRITE):
            raise APDUValueError("unsoported APCI")

        if size and len(data) != size or not size and (len(data) != 1 or data[0] & 0x3f != data[0]):
            raise APDUValueError("incompatible data/size values")

        aPDU = bytearray(2 + size)
        if size:
            aPDU[0] = (apci >> 8) & 0xff
            aPDU[1] = apci & 0xff
            aPDU[2:] = data
        else:
            aPDU[0] = (apci >> 8) & 0xff
            aPDU[1] = apci & 0xff | data[0] & 0x3f

        return aPDU

    @classmethod
    def getGroupValue(cls, aPDU):
        """ Extract data from given APDU
        """
        if len(aPDU) > 2:
            data = aPDU[2:]
        else:
            data = bytearray((aPDU[1] & 0x3f,))

        return data

