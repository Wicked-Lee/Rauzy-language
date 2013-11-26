import json
from Object import *
from Relation import *

#define a "parse" function to parse a rau file for a model and create all Objects and Relations
def parse(file):
	#open and then read the file
	f=open(file,'r')        #open a file for reading
	s=f.read()              #read the content of file f
	#return a python object out of a json object
	target=json.loads(s)
	f.close()
	model = Object(file.split(".")[0],target)
	return model

#writes the necessary files for this model
#One file for root object
#One file (library) for the rest objects
def toFile():
	pass

def validate(target):
	pass
	
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

	