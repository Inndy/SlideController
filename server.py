# -*- coding: utf8 -*-

import socket, thread, sys, os, uinput

try:
    device = uinput.Device([uinput.KEY_LEFT, uinput.KEY_RIGHT])
except OSError:
    print "You need root permissions to run this server."
    sys.exit(-1)

class Request:
    def __init__(self, method, path, protocol, client):
        self.method = method
        self.path = path
        self.protocol = protocol
        self.client = client
    
    def response(self, status, type, length, content):
        self.client.send("HTTP/1.1 %s\r\nContent-Type: %s\r\nContent-Length: %d\r\n\r\n%s" % (status, type, length, content))
    
    def responseHTML(self, content):
        self.response("200 OK", "text/html; charset=utf-8", len(content), content)

class ConnectionHandler:
    def __init__(self, client, client_address):
        self.client = client
        try:
            self.method, self.path, self.protocol = self.get_base_header()
        except:
            print "Invalid Request"
            return
        
        print "%s %s %s" % (self.method, self.path, self.protocol)

        req = Request(self.method, self.path, self.protocol, client)

        if req.path == "/":
            req.responseHTML(open("index.html", "r").read())
        if req.path == "/left":
            device.emit_click(uinput.KEY_LEFT)
            req.responseHTML("left")
        elif req.path == "/right":
            device.emit_click(uinput.KEY_RIGHT)
            req.responseHTML("right")
        else:
            req.response("404 Not Found", "text/html", 5, "ERROR")
        
        client.close()

    def get_base_header(self):
        buff = self.client.recv(1024)
        index = buff.find("\n")
        if index > -1:
            data = (buff[:index + 1]).split()
            if len(data) == 3:
                return data
        raise Error("Invalied Length")
        
def StartServer(ip = "0.0.0.0", port = 6677):
    """
        Start server

        -s,  --ip=<str>             Server IP
        -p,  --port=<int>           Server port
    """
    mysocket = socket.socket(socket.AF_INET)
    mysocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    mysocket.bind((ip, port))
    print "Server is listening on %s:%d" % (ip, port)
    mysocket.listen(0)
    while True:
        try:
            thread.start_new_thread(ConnectionHandler, mysocket.accept())
        except KeyboardInterrupt:
            print "Keybaord Interrupt Catched"
            break

try:
    import clime.now
except ImportError:
    StartServer()