from abc import ABC, abstractmethod
import hashlib
import asyncio
import logging
import datetime
import enum
import socket
import os
import traceback


from responder3.utils import ServerProtocol

class ConnectionStatus(enum.Enum):
	OPENED = 0
	CLOSED = 1
	STATELESS = 3

class Connection():
	def __init__(self, soc, status, rdnsd):
		self.status      = status
		self.rdns        = ''
		self.remote_ip   = ''
		self.remote_port = ''
		self.local_ip    = ''
		self.local_port  = ''
		self.timestamp   = datetime.datetime.utcnow()

		self.remote_ip, self.remote_port = soc.getpeername()
		self.local_ip, self.local_port   = soc.getsockname()

		if self.remote_ip in rdnsd:
			self.rdns = rdnsd[self.remote_ip]
		
		else:
			try:
				self.rdns = socket.gethostbyaddr(self.remote_ip)[0]
			except Exception as e:
				pass

			rdnsd[self.remote_ip] = self.rdns


	def getremoteaddr(self):
		return (self.remote_ip, self.remote_port)

	def toDict(self):
		t = {}
		t['status']      = self.status
		t['rdns']        = self.rdns
		t['remote_ip']   = self.remote_ip
		t['remote_port'] = self.remote_port
		t['local_ip']    = self.local_ip
		t['local_port']  = self.local_port
		t['timestamp']   = self.timestamp
		return t

	def __str__(self):
		if self.rdns != '':
			return '[%s] %s:%d -> %s:%d' % (self.timestamp.isoformat(), self.rdns, self.remote_port, self.local_ip,self.local_port )
		else:
			return '[%s] %s:%d -> %s:%d' % (self.timestamp.isoformat(), self.remote_ip, self.remote_port, self.local_ip,self.local_port )


class Result():
	def __init__(self,data = None):
		self.module    = None
		self.type      = None 
		self.client    = None
		self.user      = None
		self.cleartext = None
		self.fullhash  = None

		self.fingerprint = None

		if data is not None:
			self.parse(data)

	def parse(self,data):
		m = hashlib.sha256()
		self.module    = data['module']
		m.update(self.module.encode())
		self.type  = data['type'] 
		m.update(self.type.encode())
		self.client    = data['client']
		m.update(self.client.encode())
		self.user      = data.get('user')
		if self.user is not None:
			m.update(self.user.encode())
		self.cleartext = data.get('cleartext')
		if self.cleartext is not None:
			m.update(self.cleartext.encode())
		self.fullhash  = data.get('fullhash')
		##some types needs to be excluded because they relay on some form of randomness in the auth protocol, 
		##yielding different fullhash data for the same password
		if self.fullhash is not None and self.type not in ['NTLMv1','NTLMv2']:
			m.update(self.fullhash.encode())

		self.fingerprint = m.hexdigest()

	def toDict(self):
		t = {}

		t['module'] = self.module
		t['type'] = self.type
		t['client'] = self.client
		t['user'] = self.user
		t['cleartext'] = self.cleartext
		t['fullhash'] = self.fullhash

		t['fingerprint'] = self.fingerprint
		return t

	def __eq__(self, other):
		return self.fingerprint == other.fingerprint

	def __ne__(self, other):
		return self.fingerprint != other.fingerprint


class LogEntry():
	def __init__(self, level, name, msg):
		self.level = level
		self.name  = name
		self.msg   = msg

	def __str__(self):
		return "[%s] %s" % (self.name, self.msg)

class ResponderServer(ABC):
	def __init__(self):
		self.port      = None
		self.loop      = None
		self.logQ      = None
		self.settings  = None
		self.peername  = None #this is set when a connection is made!
		self.peerport  = None
		self.rdnsd     = None
		self.bind_addr = None
		self.bind_port = None
		self.bind_family = None
		self.bind_proto  = None

	def _setup(self, server, loop, logQ):
		self.bind_addr = server.bind_addr
		self.bind_port = server.bind_port
		self.bind_family = server.bind_family
		self.bind_proto  = server.proto
		self.loop      = loop
		self.logQ      = logQ
		self.settings  = server.settings
		self.rdnsd     = server.rdnsd
		self.setup()

	def run(self, ssl_context = None):
		"""
		TODO: SSL over UDP ?
		"""
		if self.bind_proto in [ServerProtocol.TCP, ServerProtocol.SSL]:
			coro = self.loop.create_server(
								protocol_factory=lambda: self.protocol(self),
								host=str(self.bind_addr), 
								port=self.bind_port,
								family=self.bind_family,
								reuse_address=True,
								reuse_port=True,
								ssl=ssl_context
			)

		elif self.bind_proto == ServerProtocol.UDP:
			coro = self.loop.create_datagram_endpoint(
							protocol_factory=lambda: self.protocol(self),
							local_addr=(str(self.bind_addr), self.bind_port),
							family=self.bind_family
			)

		return self.loop.run_until_complete(coro)

	def log(self, level, message):
		if self.peername == None:
			message = '[INIT] %s' %  message
		else:	
			message = '[%s:%d] %s' % (self.peername, self.peerport, message)
		self.logQ.put(LogEntry(level, self.modulename(), message))

	def logResult(self, resultd):
		self.logQ.put(Result(resultd))

	def logConnection(self, conn):
		self.logQ.put(conn)

	def setup(self):
		pass

	@abstractmethod
	def modulename(self):
		pass

	@abstractmethod
	def handle(self):
		pass


class ResponderProtocolTCP(asyncio.Protocol):
	
	def __init__(self, server):
		asyncio.Protocol.__init__(self)
		self._server = server
		self._con            = None
		self._buffer_maxsize = 10*1024 #if the buffer becomes bigger than this, an exception will be raised
		self._parsed_length  = None    #most TCP based protocols contain a length of the data to be read, reaching this length will trigger a call to _parsebuff
		self._transport      = None
		self._buffer         = b''


	def connection_made(self, transport):
		self._con = Connection(transport.get_extra_info('socket'), ConnectionStatus.OPENED, self._server.rdnsd)
		self._server.logConnection(self._con)
		self._server.peername, self._server.peerport = self._con.getremoteaddr()
		self._server.log(logging.INFO, 'New connection opened')
		self._transport = transport
		self._connection_made(transport)

	def data_received(self, raw_data):
		try:
			self._buffer += raw_data
			if len(self._buffer) >= self._buffer_maxsize:
				raise Exception('Input data too large!')
		
			if 'R3DEEPDEBUG' in os.environ:
				#FOR DEBUG AND DEVELOPEMENT PURPOSES ONLY!!!
				self._server.log(logging.INFO,'Buffer contents before parsing: %s' % (self._buffer.hex()))

			
			self._parsebuff()

			if 'R3DEEPDEBUG' in os.environ:
				#FOR DEBUG AND DEVELOPEMENT PURPOSES ONLY!!!
				self._server.log(logging.INFO,'Buffer contents after parsing: %s' % (self._buffer.hex()))

		
		except Exception as e:
			traceback.print_exc()
			self._server.log(logging.INFO, 'Data reception failed! Reason: %s' % str(e))
			
			

	def connection_lost(self, exc):
		self._con.status = ConnectionStatus.CLOSED
		self._server.logConnection(self._con)
		self._server.log(logging.INFO, 'Connection closed')
		self._connection_lost(exc)

	## Override this to access to connection lost function
	def _connection_lost(self, exc):
		return

	## Override this to start handling the buffer, the data is in self._buffer as a string!
	def _parsebuff():
		return

	## Override this to start handling the buffer
	def _connection_made(self, transport):
		return

class ResponderProtocolUDP(asyncio.DatagramProtocol):
	
	def __init__(self, server):
		asyncio.DatagramProtocol.__init__(self)
		self._transport      = None
		self._server         = server
		self._con            = None
		self._buffer_maxsize = 10*1024
		self._buffer         = io.BytesIO()

	def connection_made(self, transport):
		self._transport = transport

	def datagram_received(self, raw_data, addr):
		#self._con = Connection(addr, ConnectionStatus.OPENED, self._server.rdnsd)
		#self._server.logConnection(self._con)
		#self._server.peername, self._server.peerport = self._con.getremoteaddr()
		self._server.log(logging.INFO, 'New connection opened')
		self._buffer.write(raw_data)
		self._parsebuff(addr)
		self._buffer = b''

	## Override this to start handling the buffer, the data is in self._buffer as a string!
	def _parsebuff():
		return

	## Override this to start handling the buffer
	def _connection_made():
		return