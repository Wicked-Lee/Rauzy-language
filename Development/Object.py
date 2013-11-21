class Object:
	#properties dictionary
	#objects list of strings
	#relations list of strings	
	def __init__(self,name,parent,properties,objects,relations):
		self.name = name
		self.parent = parent
		self.properties = properties
		self.objects = objects
		self.relations = relations
	
	#TODO def __init__(self,nested_json):
	
	#returns a string representation of this object in JSON format
	#it must call toStr method for the relations of the Object and
	#nested Objects
	def toStr():
		pass
	
	def flatten():
		pass