#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import sys
import select
import socket
import logging
import argparse
from iking_package import *
from iking_utils import iKingUtils


# class iKingLogging(logging):
#     def __init__(self, fmt=None, datefmt=None):
#         super(fmt, datefmt)
#         # logging.__init__(fmt, datefmt)

#     def formatTime(self, record, datefmt=None):
#         ct = self.converter(record.created)
#         if datefmt:
#             s = time.strftime(datefmt, ct)
#         else:
#             t = time.strftime("%H:%M:%S", ct)
#             s = "%s,%03d" % (t, record.msecs)
#         return s


class ProxyConnection(iKingPackageCaller):

    # enable a buffer on connections with this many bytes
    MAX_BUFFER_SIZE = 1024

    # ProxyConnection class forwards data between a client and a destination socket

    def __init__(self, proxyserver, listensock, servaddr):
        self.proxyserver = proxyserver
        self.servaddr = servaddr    # the server address

        self.test_flag = False
        self.package_processer = iKingPackage(self)

        # open client and server sockets
        # client socket and address
        self.clisock, self.cliaddr = listensock.accept()
        self.clisock.setblocking(0)
        # server socket
        self.servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servsock.setblocking(0)

        # buffers for data recieved from a socket
        self.buffers = {self.clisock: bytes(), self.servsock: bytes(), "iking": bytearray(), "send": bytearray(), "plain": bytearray()}

        self.connected = False      # is the server socket connected yet

        # register sockets with server and enable read operations
        self.proxyserver.registerSocket(self.clisock, self)
        self.proxyserver.registerSocket(self.servsock, self)
        self.proxyserver.activateRead(self.clisock)
        self.proxyserver.activateRead(self.servsock)

    # return the socket on the "other end" of the connection
    def other(self, socket):
        if socket == self.clisock:
            return self.servsock
        else:
            return self.clisock

    # connect to the server connection
    def connect(self):
        # have to use socket's connect_ex because the connect is asynchronous and won't suceed immediately
        self.servsock.connect_ex(self.servaddr)

    # read data in from a socket
    def readfrom(self, s):
        # is the connection being opened by the server responding to the connect?
        if s == self.servsock and not self.connected:
            self.proxyserver.connection_count += 1
            logging.getLogger("iking_proxy") \
                .info("opened connection from %s, connection count now %d" % (str(self.cliaddr), self.proxyserver.connection_count))
            self.connected = True
            return

        # read from the socket
        capacity = ProxyConnection.MAX_BUFFER_SIZE - len(self.buffers[s])

        try:
            data = s.recv(capacity)
        except Exception:
            data = ""

        # if the read failed, close the socket (this happens when the client or server closes the connection)
        if len(data) == 0:
            logging.getLogger("iking_proxy").info("close in readfrom")
            self.close()
            return

        # buffer the read data
        self.buffers[s] += data
        self.proxyserver.activateWrite(self.other(s))

        # disable further reads if buffer is full
        capacity -= len(data)
        if capacity <= 0:
            self.proxyserver.deactivateRead(s)

    # write data out to a socket
    def writeto(self, s):
        # get the buffer containing data to be read
        buf = self.buffers[self.other(s)]

        if s == self.clisock:
            iking_buf = self.buffers["iking"]
            iking_buf.extend(bytearray(buf))

            # if not self.test_flag:
            #     self.test_flag = True
            #     iKingUtils.dump_bytearray(iking_buf, prefix="first")

            data_plain = self.buffers['plain']
            data_dec = iKingUtils.decode(iking_buf)
            data_plain.extend(data_dec)

            (data_packs, offset) = iKingPackage.extract_pack(data_plain)
            if len(data_packs):
                self.package_processer.process_data_packs(data_packs, self)
            data_plain[0:offset] = []

            dl = len(data_dec)
            if dl > 0:
                iking_buf[0:dl] = []
        else:
            send_buf = self.buffers["send"]
            send_buf.extend(bytearray(buf))

            # iKingUtils.dump_bytearray(send_buf, prefix="origin")
            iKingUtils.dump_bytearray(bytearray(buf), prefix="sendbf")
            data_dec = iKingUtils.decode(send_buf)
            iKingUtils.dump_bytearray(data_dec, prefix="send")
            dl = len(data_dec)
            if dl > 0:
                send_buf[0:dl] = []

        # write it to the socket
        written = s.send(buf)

        # remove written data from the buffer
        buf = buf[written:]
        self.buffers[self.other(s)] = buf

        # disable further writes if the buffer is empty
        if len(buf) == 0:
            self.proxyserver.deactivateWrite(s)
        # enable reads if data was written
        if written:
            self.proxyserver.activateRead(self.other(s))

    # close the connection sockets
    def close(self):
        self.package_processer.stop()
        for sock in [self.clisock, self.servsock]:
            if sock:
                self.proxyserver.deactivateRead(sock)
                self.proxyserver.deactivateWrite(sock)
                sock.close()
                self.proxyserver.unregisterSocket(sock, self)

        self.proxyserver.connection_count -= 1
        logging.getLogger("iking_proxy").info("closed connection from %s, connection count now %d" % (self.cliaddr, self.proxyserver.connection_count))

    def beforePackProcess(caller, pack):
        pass

    def doPackProcess(caller, pack, dictionary):
        # reload(sys.modules['iking_package'])
        # from iking_package import iKingPackage
        t = pack['type']
        caller.package_processer.process_pack(t, pack)

    def afterPackProcess(caller, pack):
        pass


class iKingProxy(object):

    def __init__(self, host, port, serverhost, serverport):
        self.address = (host, port)
        self.server = (serverhost, serverport)
        self.listensock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listensock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listensock.bind(self.address)
        self.listensock.listen(5)
        self.connections = {}                # map from a socket to a ProxyConnection
        self.readsockets = []                # all sockets which can be read
        self.writesockets = []               # all sockets which can be written
        self.allsockets = [self.listensock]  # all opened sockets
        self.connection_count = 0            # count of all active connections

    def run(self):
        loop = 0
        while True:
            # block until there is some activity on one of the sockets, timeout every 60 seconds by default
            r, w, e = select.select(
                [self.listensock] + self.readsockets,
                self.writesockets,
                self.allsockets,
                60)
            loop += 1
            # handle any reads
            for s in r:
                if s is self.listensock:
                    # open a new connection
                    self.open()
                else:
                    if s in self.connections:
                        self.connections[s].readfrom(s)
            # handle any writes
            for s in w:
                if s in self.connections:
                    self.connections[s].writeto(s)
            # handle errors (close connections)
            for s in e:
                if s in self.connections:
                    self.connections[s].close()

        self.sock.close()
        self.sock = None

    def activateRead(self, sock):
        if sock not in self.readsockets:
            self.readsockets.append(sock)

    def deactivateRead(self, sock):
        if sock in self.readsockets:
            self.readsockets.remove(sock)

    def activateWrite(self, sock):
        if sock not in self.writesockets:
            self.writesockets.append(sock)

    def deactivateWrite(self, sock):
        if sock in self.writesockets:
            self.writesockets.remove(sock)

    def registerSocket(self, sock, conn):
        self.connections[sock] = conn
        self.allsockets.append(sock)

    def unregisterSocket(self, sock, conn):
        del self.connections[sock]
        self.allsockets.remove(sock)

    # open a new proxy connection from the listening socket
    def open(self):
        conn = ProxyConnection(self, self.listensock, self.server)
        conn.connect()


if __name__ == '__main__':
    parse = argparse.ArgumentParser()
    parse.add_argument('--local', '-l', help='local listener', dest='proxy', default='0.0.0.0:4321', type=str)
    # parse.add_argument('--server', '-s', help='game server', dest='dest', default='112.121.109.160:4321', type=str)
    parse.add_argument('--server', '-s', help='game server', dest='dest', default='223.203.3.254:4321', type=str)
    args = parse.parse_args()

    proxy = args.proxy.split(":")
    dest = args.dest.split(":")
    proxyhost = proxy[0]
    proxyport = int(proxy[1])
    serverhost = dest[0]
    serverport = int(dest[1])

    logger = logging.getLogger('iking_proxy')
    logger.setLevel(logging.INFO)
    hdlr = logging.StreamHandler()
    hdlr.setLevel(logging.INFO)
    hdlr.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(hdlr)

    server = iKingProxy(proxyhost, proxyport, serverhost, serverport)
    server.run()
