from random import randint

class Wuerfel:
	def __init__(self, seiten):
		self.seiten = max(4,seiten)


	def werfen(self):
		return randint(1, self.seiten)
	
	def get_seiten(self):
		return self.seiten
	
	def set_seiten(self, seiten):
		if seiten > 3:
			self.seiten = seiten

class Held:
	def __init__(self, x,y,r,w):
		self.x = y
		self.y = x
		self.richtung = "up"
		self.name = "Mc Dummy"
		self.weiblich = not w
		self.typ = "Held"

	def geh(self):
		print("[",self.name, "] Nö!")

	def links(self):
		print("[",self.name, "] Nä!")

	def rechts(self):
		print("[",self.name, "] Auf keinen fall")
	
	def zurueck(self):
		print("[",self.name, "] Ich glaub du spinnst.")

	