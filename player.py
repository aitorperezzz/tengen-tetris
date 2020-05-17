# The player class stores a socket id, a name and the position of the next
# piece that will be delivered.
class Player:
	def __init__(self):
		self.id = None
		self.name = None
		self.position = 0

	def getId(self):
		return self.id

	def setId(self, socketId):
		self.id = socketId

	def getPosition(self):
		return self.position

	def setPosition(self, position):
		self.position = position
