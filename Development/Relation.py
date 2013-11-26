class Relation:
	def __init__(self,name,parent,sources,targets,directional):
		self.name = name
		self.parent = parent
		self.sources = sources
		self.targets = targets
		self.directional = directional
	
	def __init__(self,name,nested_json):
		self.name = name
		if "extends" in nested_json.keys() :
			self.parent = nested_json["extends"]
		else :
			self.parent = ""
		#sources must be an array
		if "from" in nested_json.keys() :
			sources = []
			for obj in nested_json['from'] :
				sources.append(obj)	
			self.sources = sources
		else :
			self.sources = []
		#targets must be an array
		if "to" in nested_json.keys() :
			targets = []
			for obj in nested_json['to'] :
				targets.append(obj)	
			self.targets = targets
		else :
			self.targets = []
		if "directional" in nested_json.keys() :
			self.directional = nested_json["directional"]
		else :
			self.directional = True
		
	
	#returns a string representation of this object in JSON format
	def toStr(self,indent):
		output = indent + "Name : " + self.name + "\n"
		if self.sources:
			output += indent + "From : [" 
			for src in self.sources:
				output+=src + ","
			output = output[:-1] + "]\n"
		if self.targets:
			output += indent + "To : [" 
			for tg in self.targets:
				output+=tg + ","
			output = output[:-1] + "]\n"
		output += indent + "Directional : " + str(self.directional) + "\n"
		return output