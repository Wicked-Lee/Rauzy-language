class Relation:
	def __init__(self,name,parent,sources,targets,directional):
		self.name = name
		self.parent = parent
		self.sources = sources
		self.targets = targets
		self.directional = directional
	
	#TODO def __init__(self,nested_json):
	
	#returns a string representation of this object in JSON format
	def toStr():
		pass