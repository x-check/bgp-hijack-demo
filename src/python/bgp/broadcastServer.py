###############################################################################
##
##  Copyright (C) 2011-2013 Tavendo GmbH
##
##  Licensed under the Apache License, Version 2.0 (the "License");
##  you may not use this file except in compliance with the License.
##  You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
##  Unless required by applicable law or agreed to in writing, software
##  distributed under the License is distributed on an "AS IS" BASIS,
##  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##  See the License for the specific language governing permissions and
##  limitations under the License.
##
###############################################################################

import sys

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import File

from autobahn.twisted.websocket import WebSocketServerFactory, \
                                       WebSocketServerProtocol, \
                                       listenWS

import fileinput
import threading
import Queue

putBool = False

class BroadcastServerProtocol(WebSocketServerProtocol):

   def onOpen(self):
      self.factory.register(self)

   def onMessage(self, payload, isBinary):
      if not isBinary:
         msg = "{} from {}".format(payload.decode('utf8'), self.peer)
         self.factory.broadcast(msg)

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
		reactor.callLater(2, self.tick)

	def register(self, client):
		# if this bool is true, then the queue is filled
		# becomes true, when a client is registered
		global putBool
		putBool = True

		if not client in self.clients:
			print("registered client {}".format(client.peer))
			self.clients.append(client)

	def unregister(self, client):
		if client in self.clients:
			print("unregistered client {}".format(client.peer))
			self.clients.remove(client)

		# set bool to false, so that queue is not filled anymore and is cleared
		if len(self.clients) == 0:
			global putBool
			putBool = False
			MyFileinputReader.queue.queue.clear()

	def broadcast(self, msg):
		#print("broadcasting message '{}' ..".format(msg))
		#print "Queue size: " + str(MyFileinputReader.queue.qsize())
		if len(self.clients) > 0:
			for i in range(0,MyFileinputReader.queue.qsize()):
				message = MyFileinputReader.queue.get()
				print message
				for c in self.clients:
					c.sendMessage(message.encode('utf8'))
					#print("message sent to {}".format(c.peer))


class BroadcastPreparedServerFactory(BroadcastServerFactory):
   """
   Functionally same as above, but optimized broadcast using
   prepareMessage and sendPreparedMessage.
   """

   def broadcast(self, msg):
      #print("broadcasting prepared message '{}' ..".format(msg))
      preparedMsg = self.prepareMessage(msg)
      for c in self.clients:
         c.sendPreparedMessage(preparedMsg)
         print("prepared message sent to {}".format(c.peer))


class MyFileinputReader(threading.Thread):

	queue = Queue.Queue()

	def __init__(self):
		threading.Thread.__init__(self)

	def run(self):

		while True:
			lines = sys.stdin.readline().split("\n")

			for line in lines:
				l = line.strip()
				global putBool
				if putBool and (len(l) > 0):
					MyFileinputReader.queue.put(l)

			"""
			for line in fileinput.input():
				#print line
				global putBool
				if putBool:
					MyFileinputReader.queue.put(line)
			"""
			"""
			if MyFileinputReader.queue.qsize() % 500 == 0:
			print "Queue entries: " + str(MyFileinputReader.queue.qsize()) + "\nclear queue"
			MyFileinputReader.queue.queue.clear()
			"""


if __name__ == '__main__':

	if len(sys.argv) > 1 and sys.argv[1] == 'debug':
		log.startLogging(sys.stdout)
		debug = True
	else:
		debug = False


	thread = MyFileinputReader()
	thread.start()

	ServerFactory = BroadcastServerFactory
	#ServerFactory = BroadcastPreparedServerFactory

	factory = ServerFactory("ws://141.22.28.194:5002",
	                       debug = debug,
	                       debugCodePaths = debug)

	factory.protocol = BroadcastServerProtocol
	factory.setProtocolOptions(allowHixie76 = True)
	listenWS(factory)

	webdir = File(".")
	web = Site(webdir)
	reactor.listenTCP(8080, web)

	reactor.run()
