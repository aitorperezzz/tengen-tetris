from flask_socketio import emit

from room import Room
from database import Database

class Master:
	roomsNumber = 2

	def __init__(self):
		# Create the rooms.
		self.rooms = {}
		for i in range(self.roomsNumber):
			roomName = 'room{}'.format(i + 1)
			self.rooms[roomName] = Room(roomName)

		# Open the connection to the database.
		self.database = Database()
		self.database.initialize()

	# Logs an incoming message to the terminal.
	def logMessage(self, message, socketId):
		print('--> Received {} from {}'.format(message, socketId))

	# Bounces a message from a player to its adversary.
	def bounce(self, socketId, message, data):
		# Look for the room of this socket id.
		room = self.getRoom(socketId)
		if room == None:
			return False

		# Bounce the message inside the appropriate room.
		return room.bounce(socketId, message, data)

	# A client with a specific socket id wants to play in a specific room.
	def requestDuoGame(self, socketId, data):
		# Point to the requested room.
		room = self.rooms[data['roomName']]
		if room == None:
			print('Room {} does not exist.'.format(data['roomName']))
			emit('responseDuoGame', {'accepted': False}, room=socketId)
			return False

		# Try to join the client to the requested room.
		return self.rooms[data['roomName']].join(socketId)

	# A client already accepted in a room gets identified with a username.
	def login(self, socketId, data):
		# Find out the room this socket id belongs to.
		room = self.getRoom(socketId)
		if room == None:
			print('ERROR: login from socket id that does not belong to any room')
			return False

		# Login this client inside the room.
		return room.login(socketId, data['username'])

	# A socket id has disconnected.
	def disconnect(self, socketId):
		# Find the room of this socket id.
		room = self.getRoom(socketId)
		if room == None:
			print('Disconnect: this socket id does not belong to any room')
			return False

		return room.disconnect()

	# Returns the room of a socket id, None if not in any room.
	def getRoom(self, socketId):
		for roomName, room in self.rooms.items():
			if room.inRoom(socketId):
				return room
		return None

	# A player requests the next batch of pieces.
	def requestNextBatch(self, socketId):
		room = self.getRoom(socketId)
		if room == None:
			return False

		# Request the next batch of the appropriate room.
		return room.requestNextBatch(socketId)

	# A player sends the contents of its arena.
	def updateArena(self, socketId, data):
		return self.bounce(socketId, 'updateAdversaryArena', data)

	# A player sends the new position of its falling piece.
	def updatePiece(self, socketId, data):
		return self.bounce(socketId, 'updateAdversaryPiece', data)

	# A player wants to toggle the paused state.
	def pause(self, socketId):
		return self.bounce(socketId, 'pause', {})

	# A player has lost and notifies the other one.
	def lost(self, socketId, data):
		return self.bounce(socketId, 'lost', data)

	# A player in duo mode has decided to start again.
	def startedAgain(self, socketId):
		room = self.getRoom(socketId)
		if room == None:
			return False

		# Call the function of the appropriate room.
		return room.startedAgain(socketId)

	# A player updates the selection of a selector box.
	def updateSelector(self, socketId, data):
		return self.bounce(socketId, 'updateSelector', data)

	# A player updates the state.
	def updateState(self, socketId, data):
		return self.bounce(socketId, 'updateState', data)

	# Player submits a high score.
	def submit(self, socketId, data):
		return self.database.submitHighScore(data['username'], data['mode'], data['high'])

	# Returns the high scores of the mode requested.
	def getScores(self, mode):
		return self.database.getScores(mode)
