from error import *
class Relation:
    relations = dict()
    relations2=dict()
    comp=False
    model = False

    @staticmethod
    def addRelation(name,value):
        if not Relation.comp:
            Relation.relations[name]=value
        else:
            Relation.relations2[name]=value
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
        self.properties={}
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
        if "properties" in nested_json.keys():
            for prop in nested_json['properties']:
                self.properties[prop]=nested_json['properties'][prop]

    def toJson(self,indent):
        output = indent + "\t\"" + self.name +"\" : {\n"
        output += indent +"\t\t\"nature\" : " + "\"relation\",\n"
        if self.parent:
            output+=indent+'\t\t"extends" : "'+self.parent+'",\n'
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
        if self.directional:
            output += indent+"\t\t\"directional\" : " + str(self.directional).lower()+"\n"
        if self.properties:
            output += indent + "\t\t\"properties\" : "+indent+"{\n"
            for prop in self.properties.keys() :
                output += indent+"\t\t" +"\""+prop +"\""+" : \"" + self.properties[prop] + "\",\n"
            #erase last comma
            output = output[:-2] + "\n"
            output += indent  + "\t\t}\n"
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
            if parent.properties:
                for prop in parent.properties:
                    if prop not in self.properties.keys():
                        self.properties[prop] = parent.properties[prop]

#returns a string representation of this object in JSON format
    def toStr(self,indent):
        if indent=='flat':
            flat=True
            indent=''
        output = indent + "Name : " + self.name + "\n"
        if self.parent:
            output += indent + "extends : " + self.parent + "\n"
        if self.sources:
            output += indent + "from : ["
            for src in self.sources:
                output+=src + ","
            #erase last comma
            output = output[:-1] + "]\n"
        if self.targets:
            output += indent + "to : ["
            for tg in self.targets:
                output+=tg + ","
            #erase last comma
            output = output[:-1] + "]\n"
        if self.properties:
            output += indent + "Properties : \n"
            for prop in self.properties.keys() :
                output += indent+"\t" +prop +" : " + self.properties[prop] + "\n"
        output += indent + "directional : " + str(self.directional) + "\n"
        return output
