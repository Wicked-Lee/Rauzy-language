from error import *
class Relation:
	relations = dict()
	model = False

	@staticmethod
	def addRelation(name,value):
		Relation.relations[name]=value

	@staticmethod
	def findRelation(name):
		if name in Relation.relations.keys() :
			return Relation.relations[name]

	def __init__(self,name,parent,sources,targets,directional):
		self.name = name
		self.parent = parent
		self.sources = sources
		self.targets = targets
		self.directional = directional

	def __init__(self,name,nested_json):
		self.name = name
		self.sources = []
		self.targets = []
		self.parent = ""
		self.directional = True
		if "extends" in nested_json.keys() :
			self.parent = nested_json["extends"]
            #TODO but here we have constructed relations in Object.relations?
			par = Relation.findRelation(self.parent)
			self.inherit(par)
		#sources must be an array
		if "from" in nested_json.keys() :
			for obj in nested_json['from'] :
				self.sources.append(obj)
		#targets must be an array
		if "to" in nested_json.keys() :
			for obj in nested_json['to'] :
				self.targets.append(obj)
		if "directional" in nested_json.keys() :
			self.directional = nested_json["directional"]


	def toJson(self,indent):
		output = indent + "\t\"" + self.name +"\" : {\n"
		output += indent +"\t\t\"nature\" : " + "\"relation\",\n"
		if self.sources:
			output += indent + "\t\t\"from\" : ["
			for src in self.sources:
				output += "\"" + src +"\","
			#erase last comma
			output = output[:-1]
			output += "],\n"
		if self.targets:
			output += indent + "\t\t\"to\" : ["
			for tg in self.targets:
				output += "\"" + tg +"\","
			#erase last comma
			output = output[:-1]
			output += "],\n"
		output += indent+"\t\t\"directional\" : " + str(self.directional).lower()+"\n"
		output += indent + "\t\t}"
		return output

	def inherit(self,parent):
		if parent :
			if parent.sources:
				for src in parent.sources :
					self.sources.append(src)
			if parent.targets:
				for tg in parent.targets:
					self.targets.append(tg)
			if not parent.directional:
				self.directional = parent.directional

	#returns a string representation of this object in JSON format
	def toStr(self,indent):
		output = indent + "Name : " + self.name + "\n"
		if self.parent:
			output += indent + "extends : " + self.parent + "\n"
		if self.sources:
			output += indent + "From : ["
			for src in self.sources:
				output+=src + ","
			#erase last comma
			output = output[:-1] + "]\n"
		if self.targets:
			output += indent + "To : ["
			for tg in self.targets:
				output+=tg + ","
			#erase last comma
			output = output[:-1] + "]\n"
		output += indent + "Directional : " + str(self.directional) + "\n"
		return output
