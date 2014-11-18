#!/usr/bin/env python3.4
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory
import asyncio

class MyServerProtocol(WebSocketServerProtocol):
  def onConnect(self, request):
    print("Client connecting: {0}".format(request.peer))
  def onOpen(self):
    print("WebSocket connection open.")
    self.factory.register(self)
  def onMessage(self, payload, isBinary):
    if isBinary:
      print("Binary message received: {0} bytes".format(len(payload)))
    else:
      print("Text message received: {0}".format(payload.decode('utf8')))
    self.factory.broadcast(payload.decode())
  def onClose(self, wasClean, code, reason):
    print("WebSocket connection closed: {0}".format(reason))
    self.factory.unregister(self)
  def connectionLost(self, reason):
    WebSocketServerProtocol.connectionLost(self, reason)
    self.factory.unregister(self)

class BroadcastServerFactory(WebSocketServerFactory):
  """
  Simple broadcast server broadcasting any message it receives to all
  currently connected clients.
  """
  def __init__(self, url, debug = False, debugCodePaths = False):
    WebSocketServerFactory.__init__(self, url, debug = debug, debugCodePaths = debugCodePaths)
    self.clients = []
    self.tickcount = 0
    self.tick()

  def tick(self):
    self.tickcount += 1
    self.broadcast("tick %d from server" % self.tickcount)

  def register(self, client):
    if not client in self.clients:
      print("registered client {}".format(client.peer))
      self.clients.append(client)

  def unregister(self, client):
    if client in self.clients:
      print("unregistered client {}".format(client.peer))
      self.clients.remove(client)

  def broadcast(self, msg):
    print("broadcasting message '{}' ..".format(msg))
    for c in self.clients:
      c.sendMessage(msg.encode('utf8'))
      print("message sent to {}".format(c.peer))
    
if __name__ == '__main__':
  factory = BroadcastServerFactory("ws://localhost:9000", debug = False)
  factory.protocol = MyServerProtocol
  loop = asyncio.get_event_loop()
  coro = loop.create_server(factory, '0.0.0.0', 9000)
  server = loop.run_until_complete(coro)
  try:
    loop.run_forever()
  except KeyboardInterrupt: pass
  finally:
    server.close()
    loop.close()
