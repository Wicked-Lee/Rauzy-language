import json
from Object import *
from Relation import *
from error import *
from warning import *
#define a "parse" function to parse a rau file for a model and create all Objects and Relations
def parse(file):
	#open and then read the file
	f=open(file,'r')        #open a file for reading
	s=f.read()              #read the content of file f
	#return a python object out of a json object
	target=json.loads(s)
	f.close()
	#val_root(target)
	model = Object(file.split(".")[0],target)
	return model

#writes the necessary files for this model
#One file for root object
#One file (library) for the rest objects
def toFile():
	pass

#TODO handle "Error 01: xx in the xx not defined!"
#handle "Error 05:the nature of xx is not correct!"
#handle "Error 07:Redundant definition of xx!"
#handle "Warning 02:Detect of a library member in xx, but xx is not the root object."
#handle "Warning 03: "objects" and "relations" in object A will be overriden by these of object B as A extends B"
def val_root(target,isroot):
	 keys=target.keys()
	 err_str=""
	 war_str=""
         if 'nature' is not in keys:
                 err_str+='Error01: the field [nature] is not defined in the root object!\n')
         if 'objects' is in keys and target['objects'] is not '':
                 for key in target['objects'].keys():
                         val_root(target['objects'][key],False)
        if 'relations' is in keys and target['relations'] is not '' and isroot:
                for key in target['relations'].keys():
                        if 'nature' is not in target['relations'][key]:
                                err_str+='Error01: the field [nature] is not defined in root[relations]['+key+']\n'
                        if 'from' is not in target['relations'][key]:
                                err_str+='Error01: the field [from] is not defined in root[relations]['+key+']\n'
                        if 'to' is not in target['relations'][key]:
                                err_str+='Error01: the field [to] is not defined in root[relations]['+key+']\n'
                        if 'directional' is not in target['relations'][key]:
                                err_str+='Error01: the field [directional] is not defined in root[relations]['+key+']\n'
        try:
                if err_str is not "":
                        raise error(err_str)
        except error as e:
                e.toStr()
        try:
                if war_str is not "":
                        raise warning(war_str)
        except warning as w:
                w.toStr()
                	
#prints the model in screen
def printModel():
	print "Model"
	print model.toStr("")

#print parse("Bank.rau")
#root Object
model = parse("Bank.rau")
printModel()
print model.toJson("")

#print Object.objects
#print Object.relations
#print model["objects"]

	
