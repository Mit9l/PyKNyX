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

Group data service management

Implements
==========

 - B{GroupListener}

Documentation
=============

This is the base class for L{Group<pyknyx.core.group>} listeners.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""

from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)


class GroupListener(object):
    """ GroupListener class
    """
    def __init__(self):
        """ Init the GroupListener object
        """
        super(GroupListener, self).__init__()

    def onWrite(self, src, data):
        """
        """
        raise NotImplementedError

    def onRead(self, src):
        """
        """
        raise NotImplementedError

    def onResponse(self, src, data):
        """
        """
        raise NotImplementedError

