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

Application management

Implements
==========

 - B{FunctionalBlockValueError}
 - B{FunctionalBlock}

Documentation
=============

B{FunctionalBlock} is one of the most important object of B{pKNyX} framework, after L{Datapoint<pyknyx.core.datapoint>}.

Usage
=====

@author: Frédéric Mantegazza
@copyright: (C) 2013-2015 Frédéric Mantegazza
@license: GPL
"""

from pyknyx.common.exception import PKNyXValueError
from pyknyx.common.utils import reprStr
from pyknyx.common.frozenDict import FrozenDict
from pyknyx.services.logger import logging; logger = logging.getLogger(__name__)
from pyknyx.services.notifier import Notifier
from pyknyx.core.datapoint import Datapoint
from pyknyx.core.groupObject import GroupObject


class FunctionalBlockValueError(PKNyXValueError):
    """
    """


class FunctionalBlock(object):
    """ FunctionalBlock class

    The Datapoints of a FunctionalBlock must be defined in sub-classes, as class dict, and named B{DP_xxx}. They will be
    automatically instanciated as real L{Datapoint} objects, and added to the B{_datapoints} dict.

    Same for GroupObject.

    @ivar _name: name of the device
    @type _name:str

    @ivar _desc: description of the device
    @type _desc:str

    @ivar _params: additional user params
    @type _params: dict

    @ivar _datapoints: Datapoints exposed by this FunctionalBlock
    @type _datapoints: dict of L{Datapoint}

    @ivar _groupObjects: GroupObjects exposed by this FunctionalBlock
    @type _groupObjects: dict of L{GroupObject}
    """
    def __new__(cls, *args, **kwargs):
        """ Init the class with all available types for this DPT
        """
        self = super(FunctionalBlock, cls).__new__(cls)

        # Retrieve all parents classes, to get all objects defined there
        classes = cls.__mro__

        # class objects named B{DP_xxx} are treated as Datapoint and added to the B{_datapoints} dict
        datapoints = {}
        for cls_ in classes:
            for key, value in cls_.__dict__.items():
                if key.startswith("DP_"):
                    logger.debug("FunctionalBlock.__new__(): %s=(%s)" % (key, repr(value)))
                    name = value['name']
                    if name in datapoints:
                        raise FunctionalBlockValueError("duplicated Datapoint (%s)" % name)
                    datapoints[name] = Datapoint(self, **value)
        self._datapoints = FrozenDict(datapoints)

        # class objects named B{GO_xxx} are treated as GroupObjects and added to the B{_groupObjects} dict
        groupObjects = {}
        for cls_ in classes:
            for key, value in cls_.__dict__.items():
                if key.startswith("GO_"):
                    logger.debug("FunctionalBlock.__new__(): %s=(%s)" % (key, repr(value)))
                    try:
                        datapoint = self._datapoints[value['dp']]
                    except KeyError:
                        raise FunctionalBlockValueError("unknown datapoint (%s) in %s.%s" % (value['dp'],cls,key))
                    name = datapoint.name
                    if name in groupObjects:
                        raise FunctionalBlockValueError("duplicated GroupObject (%s)" % name)

                    # Remove 'dp' key from GO_xxx dict
                    # Use a copy to let original untouched
                    value_ = dict(value)
                    value_.pop('dp')
                    groupObjects[name] = GroupObject(datapoint, **value_)
        self._groupObjects = FrozenDict(groupObjects)

        try:
            self._desc = cls.__dict__["DESC"]
        except KeyError:
            logger.exception("FunctionalBlock.__new__()")
            self._desc = "FB"

        return self

    def __init__(self, name, desc=None, params={}):
        """

        @param name: name of the device
        @type name: str

        @param desc: description of the device
        @type desc: str

        @param params: additional user params
        @type params: dict

        raise FunctionalBlockValueError:
        """
        super(FunctionalBlock, self).__init__()

        self._name = name

        if desc is not None:
            self._desc = "%s::%s" % (self._desc, desc)

        self._params = params

        # Call for additional user init
        self.init()

    def __repr__(self):
        return "<%s(name='%s', desc='%s')>" % (reprStr(self.__class__), self._name, self._desc)

    def __str__(self):
        return "<%s('%s')>" % (reprStr(self.__class__), self._name)

    def init(self):
        """ Additional user init
        """
        pass

    @property
    def name(self):
        return self._name

    @property
    def desc(self):
        return self._desc

    @property
    def params(self):
        return self._params

    @property
    def dp(self):
        return self._datapoints

    @property
    def go(self):
        return self._groupObjects

    def notify(self, dp, oldValue, newValue):
        """ Notify the functional block of a datapoint value change

        The functional block must trigger all methods bound to this notification with xxx.notify.datapoint()

        @param dp: name of the datapoint which sent this notification
        @type dp: str

        @param oldValue: old value of the datapoint
        @type oldValue: depends on the datapoint DPT

        @param newValue: new value of the datapoint
        @type newValue: depends on the datapoint DPT

        @todo: use an Event as param
        """
        logger.debug("FunctionalBlock.notify(): dp=%s, oldValue=%s, newValue=%s" % (dp, oldValue, newValue))

        Notifier().datapointNotify(self, dp, oldValue, newValue)

