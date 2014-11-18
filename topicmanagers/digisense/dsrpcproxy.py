import httplib
import xmlrpclib
import socket
import errno
import sys
from TelemetryLayer.lib.tllogging import tlLogging as Log

from PyQt4.QtCore import QObject

# recipie from mtasic85
# http://stackoverflow.com/questions/372365/set-timeout-for-xmlrpclib-serverproxy

class TimeoutHTTPConnection(httplib.HTTPConnection):
    def connect(self):
        httplib.HTTPConnection.connect(self)
        self.sock.settimeout(self.timeout)


class TimeoutHTTP(httplib.HTTP):
    _connection_class = TimeoutHTTPConnection

    def set_timeout(self, timeout):
        self._conn.timeout = timeout



class TimeoutTransport(xmlrpclib.Transport):


    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, use_datetime=0):
        xmlrpclib.Transport.__init__(self, use_datetime)
        self._timeout = timeout

    def make_connection(self, host):
        # If using python 2.6, since that implementation normally returns the 
        # HTTP compatibility class, which doesn't have a timeout feature.
        if sys.version_info <= (2,6):
            host, extra_headers, x509 = self.get_host_info(host)
            return httplib.HTTPConnection(host, timeout=self._timeout)
        else:
            conn = xmlrpclib.Transport.make_connection(self, host)
            conn.timeout = self._timeout
            return conn

    #def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *args, **kwargs):
    #    xmlrpclib.Transport.__init__(self, *args, **kwargs)
    #    self.timeout = timeout
    #
    #def make_connection(self, host):
    #    if self._connection and host == self._connection[0]:
    #        return self._connection[1]
    #
    #    chost, self._extra_headers, x509 = self.get_host_info(host)
    #    self._connection = host, httplib.HTTPConnection(chost)
    #    return self._connection[1]

    def _close(self):
        Log.debug("Closing connection")
        if self._connection:
            self._connection[1].close()
            raise ValueError("Closed")


class dsRPCProxy(QObject):
    """
    Interface to the RPC server
    """

    timeout = 3

    def __init__(self, host, port):
        QObject.__init__(self)
        self.uri = "http://" + str(host) + ":" + str(port)

    def connect(self):
        Log.debug("Connecting RPC")
        self.transport = TimeoutTransport(timeout=self.timeout)
        self.socket = xmlrpclib.ServerProxy(self.uri, transport=self.transport, allow_none=True)
        return self.socket
        
