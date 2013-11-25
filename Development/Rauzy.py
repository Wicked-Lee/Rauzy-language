import json
from Object import *
from Relation import *

#define a "parse" function to parse a rau file for a model and create all Objects and Relations
def parse(file):
	#open and then read the file
	f=open(file,'r')        #open a file for reading
	s=f.read()              #read the content of file f
	#To get rid of all the unmeSaning symbols after reading
	s=s.replace("\n","")    #replace the string "\n" by ""
	s=s.replace("\t","")    #replace the string "\t" by ""
	s=" ".join(s.split())   #remove the duplicated spaces
	#return a python object out of a jason object
	target=json.loads(s)
	f.close()
	model = Object(file.split(".")[0],target)
	return model
	#TODO parse json object to fill the model and library objects

#writes the necessary files for this model
#One file for root object
#One file (library) for the rest objects
def toFile():
	pass

#finds the Object with the given name	
def findObject(name):
	for object in objects:
		if object.name == name:
			return object
	
#finds the relation with the given name		
def findRelation(name):
	for relation in relations:
		if relation.name == name:
			return relation

#prints the model in screen
def printModel():
	pass

#print parse("Bank.rau")
#root Object
model = parse("Bank.rau")
print Object.objects
#print model["objects"]
print "it works!"


	