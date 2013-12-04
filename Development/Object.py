import json
from error import *
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
	#TODO handle "Error 03: the object xx is not defined !"
	@staticmethod	
	def findObject(name):
            try:
		if name in Object.objects.keys() :
			return Object.objects[name]
		else:
                        raise error("Error 03: the object "+name+" is not defined !")
            except error as e:
                e.toStr()
		
	#finds the relation with the given name	
        #TODO handle "Error 04:the relation xx is not defined !"
	@staticmethod
	def findRelation(name):
            try:
		if name in Object.relations.keys() :
			return Object.relations[name]
		else:
                        raise error("Error 04:the relation "+name+" is not defined !")
            except error as e:
                    e.toStr()
	
	@staticmethod
	def addObject(name,object):
		Object.objects[name]=object
	@staticmethod
	def addRelation(name,value):
		Object.relations[name]=value

	#handle "Error 02:the library file xx is not found!"
	@staticmethod
	def readLibrary(file):
		f=open(file,'r')        #open a file for reading
		s=f.read()              #read the content of file f
		#To get rid of all the unmeaningful symbols after reading
                s=s.replace("\n","")    #replace the string "\n" by ""
                s=s.replace("\t","")    #replace the string "\t" by ""
                s=" ".join(s.split())   #remove the duplicated spaces
		#return a python object out of a json object
		target=json.loads(s)
		f.close()
		#val_lib(file,target)
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
					Object.relationsLib[relationName]=relation
    

#TODO handle "Error 01: xx in the xx not defined!"
#handle "Error 05:the nature of xx is not correct!"
#handle "Error 06:A cyclic dependency detected! The cycle is xx0-(include)->xx1-(extends)->xx2-(include)->..-(extends)->xx0."
#handle "Error 07:Redundant definition of xx!"
#handle "Error 08:Incorrect library file format:(xx not recognized)!" 
#handle "Warning 01:xx should not be defined in a libray relation."
#handle "Warning 03: 'objects' and 'relations' in object A will be overriden by these of object B as A extends B"
	@staticmethod
	def val_lib(tarname,target,islib,list_obj,list_rel):
                err_str=""
                war_str=""
                if 'nature' not in target.keys() or target['nature']=='':
                        err_str+='Error01: the field [nature] is not defined in the library '+tarname+'!\n'
                elif target["nature"] != "library" and islib:
                        err_str+='Error 05:the nature of library '+tarname+' is not correct!\n'
                elif target['nature'] !='object' and not islib:
                        err_str+='Error 05:the nature of object '+tarname+' is not correct!\n'
                if 'objects' in target.keys() and target['objects'] != '':
                        for key in target['objects'].keys():
                                #with below, we can check "Error 07" at the different levels
                                if key in list_obj:
                                        err_str+='Error 07:Redundant definition of object '+key+'!\n'
                                else:
                                        list_obj.append(key)
                                valstr=val_lib(key,target['objects'][key],False,list_obj,list_rel)
                                err_str+=valstr[0]
                                war_str+=valstr[1]
                if islib and 'relations' in target and target['relations']!='':
                        for key in target['relations'].keys():
                                if 'nature' not in target['relations'][key]:
                                        err_str+='Error01: the field [nature] is not defined in'+tarname+'[relations]['+key+']\n'
                                elif target['relations'][key]['nature'] != 'relation':
                                        err_str+='Error 05:the nature of'+tarname+'[relations]['+key+'] is not correct!\n'
                                if 'from' in target['relations'][key]:
                                        war_str+='Warning 01: the field [from] should not be defined in '+tarname+'[relations]['+key+']\n'
                                if 'to' not in target['relations'][key]:
                                        war_str+='Warning 01: the field [to] should not be defined in '+tarname+'[relations]['+key+']\n'
                                if 'directional' not in target['relations'][key]:
                                        err_str+='Error 01: the field [directional] is not defined in '+tarname+'[relations]['+key+']\n'
                if not islib and 'relations' in target and target['relations']!='':
                        for key in target['relations'].keys():
                                #with below, we can check "Error 07" at the different levels
                                if key in list_rel:
                                        err_str+='Error 07:Redundant definition of relation '+key+'!\n'
                                else:
                                        list_rel.append(key)
                                if 'nature' not in target['relations'][key]:
				        err_str+='Error 01: the field [nature] is not defined in lib['+tarname+'][relations]['+key+']\n'
                                elif target['relations'][key]['nature'] != 'relation':
                                        err_str+='Error 05:the nature of'+tarname+'[relations]['+key+'] is not correct!\n'
                                if 'from' not in target['relations'][key]:
                                        err_str+='Error 01: the field [from] is not defined in '+tarname+'[relations]['+key+']\n'
                                if 'to' not in target['relations'][key]:
                                        err_str+='Error 01: the field [to] is not defined in '+tarname+'[relations]['+key+']\n'
                                if ('extends' not in target['relations'][key] or target['relations'][key]['extends']=='') and 'directional' not in target['relations'][key]:
                                        err_str+='Error 01: the field [directional] is not defined in '+tarname+'[relations]['+key+']\n'
                if islib:
                        for key in target.keys():
                            try:
                                if key not in ['nature','objects','relations']:
                                        raise error("Error 08:Incorrect library file format: "+key+" not recognized!\n")
                            except error as e:
                                e.toStr()
                                #err_str+=e.msg
                        				
	#properties dictionary
	#objects list of strings
	#relations list of strings	
	def __init__(self,name,parent,properties,objects,relations):
		self.name = name
		self.parent = parent
		self.properties = properties
		self.objects = objects
		self.relations = relations
		self.library = None
	
	def __init__(self,name,nested_json):
		self.name = name
		self.properties = dict()
		self.relations = []		
		self.library = None
		if "library" in nested_json.keys():
			self.library = nested_json['library']
			#updates the static dictionaries for the library objects/relations
			Object.readLibrary(self.library)
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
		if self.library:
			output += indent + "\"library\" : " + "\""+self.library+"\",\n"
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
		
	
