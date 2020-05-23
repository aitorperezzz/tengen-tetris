from random import random
from math import floor
from flask_socketio import join_room, leave_room, emit

from player import Player

class Room:
	possiblePieces = ['T', 'J', 'Z', 'O', 'S', 'L', 'I']

	def __init__(self, name):
		self.name = name

		# Store information about each player.
		self.players = {
			1: Player(),
			2: Player(),
		}

		# List of the pieces both players play with.
		self.pieces = []

	# Join a client to this room.
	def join(self, socketId):
		player = None
		if self.players[1].getId() == None:
			self.players[1].setId(socketId)
			player = 1
		elif self.players[2].getId() == None:
			self.players[2].setId(socketId)
			player = 2
		else:
			print('ERROR: cannot join client to room {}. The room is full'.format(self.name))
			emit('responseDuoGame', {'accepted': False}, room=socketId)
			return False

		# Join this socket id to the web sockets room.
		join_room(self.name)
		print('Client {} accepted in room {}'.format(socketId, self.name))

		# Notify the client he has been accepted in the room.
		emit('responseDuoGame', {'accepted': True}, room=socketId)

	# Store the username of the client and notify about the next step.
	def login(self, socketId, username):
		playerNumber = self.getPlayerNumber(socketId)
		if playerNumber == None:
			print('ERROR. Trying to login a client that does not exist in room.')
			return False

		# Store the username for the appropriate player.
		self.players[playerNumber].setName(username)

		# If we still do not have both sockets and usernames, tell the client to wait.
		if self.numPlayers() != 2 or not self.bothUsernamesIntroduced():
			print('Room {} not yet full, or not both players identified'.format(self.name))
			print('Telling the client to wait')
			emit('waitForPlayer', {}, room=socketId)

		# If the room is full and I have both usernames, begin the duo game.
		else:
			print('Room {} is full and both players identified'.format(self.name))
			print('Telling both players to begin duo game')
			self.beginDuoGame()

	# A player in this room has disconnected. Empty the room.
	def disconnect(self):
		# Notify both players.
		emit('endDuoGame', {}, room=self.name)

		# Reset the players and the piece list.
		self.pieces = []
		self.players = {
			1: Player(),
			2: Player(),
		}

		print('Disconnected both players in room {}. Room is currently empty'.format(self.name))

	# Returns the number of players currently in the room.
	def numPlayers(self):
		if self.players[1].getId() == None:
			return 0
		elif self.players[2].getId() == None:
			return 1
		else:
			return 2

	# Decides if both usernames have been introduced into the data structure.
	def bothUsernamesIntroduced(self):
		if self.players[1].getName() == None or self.players[2].getName() == None:
			return False
		return True

	# Returns the player number from a socket id.
	def getPlayerNumber(self, socketId):
		if self.players[1].getId() == socketId:
			return 1
		elif self.players[2].getId() == socketId:
			return 2
		else:
			return None

	# Returns the socket id of the adversary.
	def getAdversarySocketId(self, socketId):
		if self.players[1].getId() == socketId:
			return self.players[2].getId()
		elif self.players[2].getId() == socketId:
			return self.players[1].getId()
		else:
			return None

	# Decides if the socket id is a player in this room.
	def inRoom(self, socketId):
		return self.players[1].getId() == socketId or self.players[2].getId() == socketId

	# Logs the pieces in this room to the terminal.
	def logPieces(self):
		print('Current pieces in room {}:'.format(self.name))
		print(self.pieces)

	# Starts the duo game.
	def beginDuoGame(self):
		# Create the first ten pieces and pack them.
		self.pieces = []
		for i in range(10):
			self.pieces.append(self.possiblePieces[floor(random() * len(self.possiblePieces))])
		firstPieces = {'pieces': self.pieces}
		self.logPieces()

		# Initialize the counter for both players.
		self.players[1].setPosition(10)
		self.players[2].setPosition(10)

		emit('beginDuoGame', firstPieces, room=self.name)

	# Appends the requested number of pieces to the list in this room.
	def createNewPieces(self, numPieces):
		for i in range(numPieces):
			self.pieces.append(self.possiblePieces[floor(random() * len(self.possiblePieces))])
		self.logPieces()

	# Bounce a message to the other player in this room.
	def bounce(self, socketId, message, data):
		adversarySocketId = self.getAdversarySocketId(socketId)
		if adversarySocketId == None:
			print('ERROR: cannot bounce message')
			return False

		emit(message, data, room=adversarySocketId)
		return True

	# Handles the request of a next batch from a socket id of this room.
	def requestNextBatch(self, socketId):
		# Get the player number of this socket id.
		player = self.getPlayerNumber(socketId)
		if player == None:
			print('ERROR: cannot handle next batch request. Player unknown')
			return False

		# If I do not have the ten next pieces ready, create as many as needed.
		currentPosition = self.players[player].getPosition()
		if currentPosition + 10 > len(self.pieces):
			self.createNewPieces(currentPosition + 10 - len(self.pieces))
			for i in range(len(self.pieces) - 1, currentPosition + 10):
				self.pieces.append(self.possiblePieces[floor(random() * len(self.possiblePieces))])

		# Pack the next ten pieces.
		nextBatch = {'pieces': []}
		for i in range(10):
			nextBatch['pieces'].append(self.pieces[currentPosition + i])

		# Update the position of this player.
		self.players[player].setPosition(currentPosition + 10)

		# Send the batch to the player that requested it.
		emit('nextBatch', nextBatch, room=socketId)
		return True

	# A player in this room has started again.
	def startedAgain(self, socketId):
		# Bounce the message back to the other player in the room.
		self.bounce(socketId, 'startedAgain', {})

		# Reset the piece position of this player.
		self.players[self.getPlayerNumber(socketId)].setPosition(10)
