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

Bus priority management

Implements
==========

 - B{PriorityValueError}
 - B{Priority}

Documentation
=============

Priority is used for bus frame priority.

Usage
=====

>>> from priority import Priority
>>> p = Priority('dummy')
PriorityValueError: priority level 'dummy' not in ('system', 'normal', 'urgent', 'low')
>>> p = Priority(15)
PriorityValueError: priority level 15 not in (0x00, 0x01, 0x02, 0x03)
>>> p = Priority('normal')
>>> p
<Priority('normal')>
>>> p.level
1
>>> p.strLevel
'normal'

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""


from pyknyx.common.exception import PKNyXValueError
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)


class PriorityValueError(PKNyXValueError):
    """
    """


class Priority(object):
    """ Priority handling class
    """
    CONV_TABLE = {'system': 0x00, 'normal': 0x01, 'urgent': 0x02, 'low': 0x03,
                  0x00: 'system', 0x01: 'normal', 0x02: 'urgent', 0x03: 'low'
                 }

    def __init__(self, level='low'):
        """ Create a priority object

        @param level: level of the priority
        @type level: str or int

        raise PriorityValueError:
        """
        super(Priority, self).__init__()

        if isinstance(level, str):
            try:
                level = Priority.CONV_TABLE[level]
            except KeyError:
                logger.exception("Priority.__init__()")
                raise PriorityValueError("level %r not in ('system', 'normal', 'urgent', 'low')" % repr(level))
        elif isinstance(level, int):
            if not 0x00 <= level <= 0x03:
                raise PriorityValueError("level %d not in (0x00, 0x01, 0x02, 0x03)" % level)
        else:
            raise PriorityValueError("invalid priority level (%s)" % repr(level))

        self._level = level

    def __repr__(self):
        return "<Priority('%s')>" % self.name

    def __str__(self):
        return self.name

    #def __cmp__(self, other):

    @property
    def level(self):
        return self._level

    @property
    def name(self):
        return Priority.CONV_TABLE[self._level]

