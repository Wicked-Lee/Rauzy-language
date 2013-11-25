import json
class Object:
	
	#library of objects dictionary key = object name , value = Object
	objects = dict()
	#library of relations dictionary key = relation name , value = relation value
	relations = dict()
	
	@staticmethod
	def addObject(name,object):
		Object.objects[name]=object
	@staticmethod
	def addRelation(name,value):
		Object.objects[name]=object
	
	@staticmethod
	def readLibrary(file):
		f=open(file,'r')        #open a file for reading
		s=f.read()              #read the content of file f
		#To get rid of all the unmeSaning symbols after reading
		s=s.replace("\n","")    #replace the string "\n" by ""
		s=s.replace("\t","")    #replace the string "\t" by ""
		s=" ".join(s.split())   #remove the duplicated spaces
		#return a python object out of a jason object
		target=json.loads(s)
		f.close()
		for key in target.keys():			
			if key == "objects":
				for objectName in target[key].keys():
					object = Object(objectName,target[key][objectName])
					Object.addObject(objectName,object)
	
     	
	#properties dictionary
	#objects list of strings
	#relations list of strings	
	def __init__(self,name,parent,properties,objects,relations):
		self.name = name
		self.parent = parent
		self.properties = properties
		self.objects = objects
		self.relations = relations
	
	def __init__(self,name,nested_json):
		self.name = name
		if "library" in nested_json.keys():
			file = nested_json['library']
			#updates te static dictionaries for the library objects/relations
			Object.readLibrary(file)
		if 'extends' in nested_json.keys():
			self.parent = nested_json["extends"]
		else :
			self.parent = ""
		if 'properties' in nested_json.keys():
			self.properties = nested_json["properties"]
		else :
			self.properties = []
		#objects must be an array
		if 'objects' in nested_json.keys():
			self.objects = nested_json['objects']
		else :
			self.objects = []
		#relations must be an array
		if 'relations' in nested_json.keys():
			self.relations = nested_json['relations']
		else :
			self.relations = []
		
		print self.objects
		print self.relations
		print self.properties
		print self.parent
		print name
	
	#returns a string representation of this object in JSON format
	#it must call toStr method for the relations of the Object and
	#nested Objects
	def toStr():
		pass
	
	def flatten():
		pass
		
	