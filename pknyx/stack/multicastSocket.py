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

Implements
==========

 - B{MulticastSocket}
 - B{McastSockValueError}

Documentation
=============

Usage
=====

@author: Frédéric Mantegazza
@author: Jakub Wroniecki
@copyright: (C) 2013 Frédéric Mantegazza
@copyright: (C) 2009 Jakub Wroniecki, STANSAT
@license: GPL
"""

__revision__ = "$Id$"

import socket
import struct

from pknyx.common.exception import PKNyXValueError
from pknyx.services.logger import Logger


class McastSockValueError(PKNyXValueError):
    """
    """


class MulticastSocket(socket.socket):  # @todo: split in 2 classes
    """ Multicast socket
    """
    def __init__(self, port, address="", timeout=1):
        """

        If address is given, the socket will acts as sender to this address, otherwise the socket will acts as receiver.
        In this case, call joinGroup() to tell which address to listen to.
        """
        super(MulticastSocket, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        self._port = port
        self._address = address

        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            Logger().exception("MulticastSocket.__init__(): system doesn't support SO_REUSEPORT", debug=True)
        self.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 32)
        self.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)

        self.settimeout(timeout)

        self._bind()

    def _bind(self):
        """
        """
        self._sock.bind((self._address, self._port))

    @property
    def port(self):
        return self._port

    @property
    def address(self):
        return self._address

    @property
    def localPort(self):
        raise NotImplementedError

    @property
    def localAddress(self):
        raise NotImplementedError

    def joinGroup(self, address):
        """ Listen to the given multicast address
        """
        if self._address:
            Logger().warning("MulticastSocket.joinGroup(): socket already used as sender (bound to %s)" % self._address)

        multicast = ord(socket.inet_aton(address)[0]) in range(224, 240)
        if not multicast:
            raise McastSockValueError("address is not a multicast destination (%s)" % repr(address))

        value = struct.pack("=4sl", socket.inet_aton(address), socket.INADDR_ANY)
        self.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, value)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, value)

    def leaveGroup(self, address):
        """
        """
        value = struct.pack("=4sl", socket.inet_aton(address), socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_DROP_MEMBERSHIP, value)

    def transmit(self, data, address=0):
        """
        """
        if address:
            self._address = address
        if self._address:
            length = 0
            while length < len(data):
                l = self.sendto(data, (self._address, self._port))
                length += l
        else:
            raise McastSockValueError("destination address not set")

    def receive(self):
        """
        """
        return self.recvfrom(1024)


class MulticastSocketBase(socket.socket):
    """ Multicast socket
    """
    def __init__(self, localAddr, localPort, ttl=32, loop=1):
        """
        """
        super(MulticastSocketBase, self).__init__(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

        self._localAddr = localAddr
        self._localPort = localPort
        self._ttl= ttl
        self._loop = loop

        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except:
            Logger().exception("MulticastSocketBase.__init__(): system doesn't support SO_REUSEPORT", debug=True)
        self.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, ttl)
        self.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, loop)

        self._bind()

    def _bind(self):
        """
        """
        raise NotImplementedError

    @property
    def localAddress(self):
        return self._localAddr

    @property
    def localPort(self):
        return self._localPort


class MulticastSocketReceive(MulticastSocketBase):
    """
    """
    def __init__(self, localAddr, mcastAddr, mcastPort, timeout=1, ttl=32, loop=1):
        """
        """
        super(MulticastSocketReceive, self).__init__(localAddr, mcastPort, ttl, loop)

        multicast = ord(socket.inet_aton(mcastAddr)[0]) in range(224, 240)
        if not multicast:
            raise McastSockValueError("address is not a multicast destination (%s)" % repr(mcastAddr))

        self.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(self._localAddr))
        #value = struct.pack("=4sl", socket.inet_aton(mcastAddr), socket.INADDR_ANY)
        self.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(mcastAddr) + socket.inet_aton(self._localAddr))

        self.settimeout(timeout)

    def _bind(self):
        """
        """
        self._sock.bind(("", self._localPort))

    def receive(self):
        """
        """
        return self.recvfrom(1024)


class MulticastSocketTransmit(MulticastSocketBase):
    """
    """
    def __init__(self, localAddr, localPort, mcastAddr, mcastPort, ttl=32, loop=1):
        """
        """
        super(MulticastSocketTransmit, self).__init__(localAddr, localPort, ttl, loop)

        self._mcastAddr = mcastAddr
        self._mcastPort = mcastPort

    def _bind(self):
        """
        """
        self._sock.bind((self._localAddr, self._localPort))

    def transmit(self, data):
        """
        """
        length = 0
        while length < len(data):
            l = self.sendto(data, (self._mcastAddr, self._mcastPort))
            length += l


if __name__ == '__main__':
    import unittest

    # Mute logger
    Logger().setLevel('error')


    class MulticastSocketTestCase(unittest.TestCase):

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def test_constructor(self):
            pass


    unittest.main()
