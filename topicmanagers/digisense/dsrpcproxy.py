import httplib
import xmlrpclib
import socket
import errno
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
    
    def __init__(self, timeout=socket._GLOBAL_DEFAULT_TIMEOUT, *args, **kwargs):
        xmlrpclib.Transport.__init__(self, *args, **kwargs)
        self.timeout = timeout

    def make_connection(self, host):
        if self._connection and host == self._connection[0]:
            return self._connection[1]
        
        chost, self._extra_headers, x509 = self.get_host_info(host)
        self._connection = host, httplib.HTTPConnection(chost)
        return self._connection[1]

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
    def __init__(self,host,port):
        self.uri = "http://" + str(host) + ":" + str(port)

    def connect(self):
        Log.debug("Connecting RPC")
        self.transport = TimeoutTransport(timeout=self.timeout)
        self.socket = xmlrpclib.ServerProxy(self.uri, transport=self.transport, allow_none=True)
        return self.socket
        
