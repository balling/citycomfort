class Point:
	def __init__(self, x, y):
		self.x=x
		self.y=y

	def __add__(self,other):
		x = self.x + other.x
		y = self.y + other.y
		return Point(x,y)

	def __str__(self):
		return "Point(x=%s, y=%s)" % (self.x, self.y)

	__repr__=__str__