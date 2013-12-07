import json
import os
from Object import *
from Relation import *
from error import *
from warning import *

#define a "parse" function to parse a rau file for a model and create all Objects and Relations
def dupe_checking_hook(pairs):
    result = dict()
    for key,val in pairs:
        try:
            if key in result:
                raise error('Error 07:Redundant definition of '+key+'!\n')
            result[key] = val
        except error as e:
            e.toStr()
    return result

def parse(file):
	Object.folder = ""	
	Object.model = False
	model = None
	folders = file.split("/")	
	for i in range(0,len(folders)-1):
		Object.folder += folders[i] +"/"
	#open and then read the file
	f=open(file,'r')        #open a file for reading
	s=f.read()              #read the content of file f
	#return a python object out of a json object
	#with object_pairs_hook method, we can check "Error 07" at the same level
	target=json.loads(s,object_pairs_hook=dupe_checking_hook)
	if "library" in target.keys():
		Object.readLibrary(target['library'])
	f.close()
    #To handle all the jason file format errors and warnings
    #err_str,war_str=val_root(file,target,True)[0:2]
	err_str,war_str=val_root(file,target,True,[],[])
	try:
		if err_str != "":
			raise error(err_str)
		else:
			Object.model = True
			model = Object(file.split(".")[0],target)
	except error as e:
		e.toStr()
	try:
		if war_str != "":
			raise warning(war_str)
	except warning as w:
		w.toStr()
    #TO return the constructed model    
	return model

#writes the necessary files for this model
#One file for root object
#One file (library) for the rest objects
def toFile(folder):
	if not os.path.exists(folder):
		os.makedirs(folder)
	f = open(folder+'/'+model.name+'.rau','w')
	f.write(model.toJson(""))
	lib = open(folder + '/'+model.library,'w')
	library = "{\n \"nature\" : \"library\", \n \"objects\" : \n{\n"
	for obj in Object.objectsLib:
		library += "\t\""+obj+"\" : \n" + Object.objectsLib[obj].toJson("\t") +",\n"
	library = library[:-2] + "\n"
	library += "\t},\n \"relations\" : \n {\n"
	for rel in Object.relationsLib:
		library += Object.relationsLib[rel].toJson("\t") + "\n"
	library += "\n}\n}"
	lib.write(library)


#TODO handle "Error 01: xx in the xx not defined!"
#handle "Error 05:the nature of xx != correct!"
#handle "Error 07:Redundant definition of xx!"
#handle "Warning 02:Detect of a library member in xx, but xx is not the root object."
#handle "Warning 03: [objects] and [relations] in object A will be overriden by these of object B as A extends B"
#tarname is name of the object(not necessarily the root object), target is the parsed file, "isroot" to signify the object is the root object or not
def val_root(tarname,target,isroot,list_obj,list_rel):
    #print(tarname,isroot)
    #print(target.keys())
    #keys=
    err_str=""
    war_str=""
    if 'nature' not in target.keys() or target['nature']=='':
        err_str+='Error01: the field [nature] is not defined in the object '+tarname+'!\n'
    elif target["nature"] != "object":
        err_str+='Error 05:the nature of object '+tarname+' is not correct!\n'
    if 'extends' in target.keys() and target['extends'] != '' and 'objects' in target.keys():
		target.pop("objects",None)
		#print("after pop",target.keys())
		war_str+='Warning 03: "objects" in object '+tarname+' will be overriden by these of object '+target['extends']+' as '+tarname+'extends'+target['extends']+'\n'
    if 'objects' in target.keys() and target['objects'] != '':
		for key in target['objects'].keys():
			#with below, we can check "Error 07" at the different levels
			if key in list_obj:
				err_str+='Error 07:Redundant definition of object '+key+'!\n'
			else:
				list_obj.append(key)
			valstr=val_root(key,target['objects'][key],False,list_obj,list_rel)
			err_str+=valstr[0]
			war_str+=valstr[1]                 
    if 'relations' in target.keys() and target['relations'] != '' and isroot:
		for key in target['relations'].keys():
			if 'nature' not in target['relations'][key]:
				err_str+='Error01: the field [nature] is not defined in root[relations]'+key+']\n'
			elif target['relations'][key]['nature'] != 'relation':
				err_str+='Error 05:the nature of'+tarname+'[relations]['+key+'] is not correct!\n'
			if 'from' not in target['relations'][key]:
				err_str+='Error01: the field [from] is not defined in '+tarname+'[relations]['+key+']\n'
			if 'to' not in target['relations'][key]:
				err_str+='Error01: the field [to] is not defined in '+tarname+'[relations]['+key+']\n'
			if ('extends' not in target['relations'][key] or target['relations'][key]['extends']=='') and 'directional' not in target['relations'][key]:
				err_str+='Error01: the field [directional] is not defined in '+tarname+'[relations]['+key+']\n'
    if 'library' in target.keys() and target['library']!='' and not isroot:
        war_str+='Warning 02:Detect of a library member in'+tarname+',but '+tarname+' is not the root object\n'
    return err_str,war_str
                    
#prints the model in screen
def printModel():
    print "Model"
    print model.toStr("")

#print parse("Bank.rau")
#root Object
#model = parse("Bank.rau")
model = None
print 'type \'help\' for help'
input = raw_input('>>')
while(input!='exit') :
	if input.startswith('read'):
		Object.objects = dict()
		Object.relations = dict()
		Object.objectsLib = dict()
		Object.relationsLib = dict()
		if len(input.split()) != 2:
			print 'usage: read <file name>'
		else :
			file = input.split()[1]
			if not os.path.exists(file):
				print 'file \'' + file + '\' does not exist!'
			else:
				model = parse(file)
	elif input == "help":
		print "Available commands"
		print 'read <file name> \t to load a model'
		print 'save <folder name> \t to save the model in a file'
		print 'print \t\t\t to print the model in the screen'
		print 'exit \t\t\t to exit'
	elif input == 'print':
		if model:
			printModel()
		else:
			print 'No model has been loaded'
	elif input.startswith('save'):		
		if len(input.split()) != 2:
			print 'usage: save <folder name>'
		else:
			folder = input.split()[1]
			toFile(folder)
	else :
		print 'type \'help\' for help'
	input = raw_input('>>')

#To test val_root
##target1=parse("Test_python/Test_Error01/Bank.rau")
##print("Test_Error01 finished!\n")
##target2=parse("Test_python/Test_Error05/Bank.rau")
##print("Test_Error05 finished!\n")
##target3=parse("Test_python/Test_Error07/Bank.rau")
##print("Test_Error07 finished!\n")
#target4=parse("Test_python/Test_Warnings/Bank.rau")
#print("Test_Warnings finished!\n")
#model = parse("Bank.rau")
#printModel()
#print model.toJson("")

#print Object.objects
#print Object.relations
#print model["objects"]

    
