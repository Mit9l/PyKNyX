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

cEMI frame management

Implements
==========

 - B{CEMIFactory}
 - B{CEMIFactoryValueError}

Documentation
=============


Usage
=====


@author: Frédéric Mantegazza
@author: B. Malinowsky
@copyright: (C) 2013-2015 Frédéric Mantegazza
@copyright: (C) 2006, 2011 B. Malinowsky
@license: GPL
"""


from pyknyx.common.exception import PKNyXValueError
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.stack.cemi.cemi import CEMIValueError


class CEMIFactoryValueError(PKNyXValueError):
    """
    """


class CEMIFactory(object):
    """ cEMI frame creation handling class
    """
    def __init__(self):
        """
        """
        super(CEMIFactory, self).__init__()

