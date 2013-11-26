import json
from Relation import *
class Object:
	
	#library of all objects dictionary key = object name , value = Object
	objects = dict()
	#library of relations dictionary key = relation name , value = relation value
	relations = dict()
	#library with only the referenced objects
	objectsLib = dict()
	#library with only the referenced relations
	relationsLib = dict()
	
	#finds the Object with the given name
	@staticmethod	
	def findObject(name):
		if name in Object.objects.keys() :
			return Object.objects[name]
		
	#finds the relation with the given name	
	@staticmethod
	def findRelation(name):
		if name in Object.relations.keys() :
			return Object.relations[name]
	
	@staticmethod
	def addObject(name,object):
		Object.objects[name]=object
	@staticmethod
	def addRelation(name,value):
		Object.relations[name]=value
	
	@staticmethod
	def readLibrary(file):
		f=open(file,'r')        #open a file for reading
		s=f.read()              #read the content of file f
		#return a python object out of a json object
		target=json.loads(s)
		f.close()
		for key in target.keys():			
			if key == "objects":
				for objectName in target[key].keys():
					object = Object(objectName,target[key][objectName])
					Object.addObject(objectName,object)
					Object.objectsLib[objectName]=object
			if key == "relations":
				for relationName in target[key].keys():
					relation = Relation(relationName,target[key][relationName]) 
					Object.addRelation(relationName,relation) 
					Object.relationsLib[objectName]=relation
     	
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
		self.properties = dict()
		self.relations = []
		if "library" in nested_json.keys():
			file = nested_json['library']
			#updates the static dictionaries for the library objects/relations
			Object.readLibrary(file)
		if 'extends' in nested_json.keys():
			self.parent = nested_json["extends"]
			par = Object.findObject(self.parent)
			self.inherit(par)
		else :
			self.parent = ""
		if 'properties' in nested_json.keys():
			newProperties = nested_json["properties"]
			for prop in newProperties.keys():
				self.properties[prop] = newProperties[prop]			
		#objects must be an array
		self.objects = []
		if 'objects' in nested_json.keys():
			for objName in nested_json['objects'].keys():
				if nested_json['objects'][objName]:
					object = Object(objName,nested_json['objects'][objName])
					self.objects.append(objName)
					Object.objects[objName] = object
				else :  # case of empty str read from a file
					f=open(objName+".rau",'r')        #open a file for reading
					s=f.read()              #read the content of file f
					#return a python object out of a json object
					target=json.loads(s)
					f.close()
					object = Object(objName,target)
					self.objects.append(objName)
					Object.objects[objName] = object
		#relations must be an array
		if 'relations' in nested_json.keys():
			for rel in nested_json['relations'] :
				if not nested_json['relations'][rel] : # case of empty str read from a file
					f=open(rel+".rau",'r')        #open a file for reading
					s=f.read()              #read the content of file f
					#return a python object out of a json object
					target=json.loads(s)
					f.close()
					relation = Relation(rel,target)
					self.objects.append(rel)
					Object.relations[rel] = relation
					self.relations.append(rel)
				if isinstance(nested_json['relations'][rel], str) :
					self.relations.append(rel)
				else :
					relation = Relation(rel,nested_json['relations'][rel])
					Object.relations[rel] = relation					
					self.relations.append(rel)
			
			
	def inherit(self,parent):
		if parent :
			self.properties = dict()
			self.objects = []
			self.relations = []
			if parent.properties:
				for prop in parent.properties :
					self.properties[prop] = parent.properties[prop]
			if parent.objects:
				for obj in parent.objects:
					self.objects.append(obj)
			if parent.relations:
				for rel in parent.relations :
					self.relations.append(rel)
	
	#returns a string representation of this object 
	def toStr(self,indent):
		output = indent + "Name : " + self.name +"\n"
		if self.parent:
			output += indent + "Extends : " + self.parent +"\n"
		if self.properties:
			output += indent + "Properties : \n" 		
			for prop in self.properties.keys() :
				output += indent+"\t" +prop +" : " + self.properties[prop] + "\n"	
		if self.objects:
			output += indent + "Objects : \n"
			for objName in self.objects :
				object = Object.findObject(objName)
				output += object.toStr(indent + "\t") + "\t"+indent + "__________________________________\n"
		if self.relations:
			output += indent + "Relations : \n"
			for relName in self.relations :
				relation = Object.findRelation(relName)
				output += relation.toStr(indent + "\t") + "\t"+indent + "__________________________________\n"		
		return output
		
	#returns a JSON representation of this object  
	def toJson(self,indent):
		output = indent + "{\n" 		 
		output += indent + "\"nature\" : " + "\"object\",\n"
		if self.parent:
			output += indent + "\"extends\" : \"" + self.parent +"\",\n"
		if self.objects:
			output += indent + "\"objects\" : "+ indent +"{\n"
			for objName in self.objects :
				output += indent + "\t\"" + objName + "\" : "
				object = Object.findObject(objName)
				output += object.toJson(indent + "\t")
				output += ",\n"
			#erase last comma
			output = output[:-2] + "\n"
			output += indent  + "},\n"
		if self.relations:
			output += indent + "\t\"relations\" : {\n"
			for rel in self.relations:
				relation = Object.findRelation(rel)
				output += relation.toJson(indent) + ",\n"
			#erase last comma
			output = output[:-2] + "\n"
			output+="\t},\n"				
		if self.properties:
			output += indent + "\"properties\" : "+indent+"{\n"
			for prop in self.properties.keys() :
				output += indent+"\t" +"\""+prop +"\""+" : \"" + self.properties[prop] + "\",\n"
			#erase last comma
			output = output[:-2] + "\n"
			output += indent  + "}\n"
		else :
			#erase last comma
			output = output[:-2] + "\n"
		output += indent + "}"
		return output
	
	#no need for that function this is done when reading
	def flatten():
		pass
		
	