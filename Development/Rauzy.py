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
    #To get rid of all the unmeaningful symbols after reading
    s=s.replace("\n","")    #replace the string "\n" by ""
    s=s.replace("\t","")    #replace the string "\t" by ""
    s=" ".join(s.split())   #remove the duplicated spaces
    #return a python object out of a json object
    target=json.loads(s)
    f.close()
    #To handle all the jason file format errors and warnings 
    err_str,war_str=val_root(file,target,True)[0:2]
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
        #TO return the constructed model
    #model = Object(file.split(".")[0],target)
    model=dict()
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
#tarname is name of the object(not necessarily the root object), target is the parsed file, "isroot" to signify the object is the root object or not
def val_root(tarname,target,isroot):
    keys=target.keys()
    err_str=""
    war_str=""
    list_obj=[]
    list_rel=[]
    if 'nature' not in keys:
            err_str+='Error01: the field [nature] is not defined in the object'+tarname+'!\n'
    elif target['nature'] is not 'object':
            err_str+='Error 05:the nature of'+tarname+'is not correct!\n'
    if 'extends' in keys and target['extends'] is not '' and 'object' in keys:
            war_str+='Warning 03: "objects" and "relations" in object '+tarname+' will be overriden by these of object '+target['extends']+' as '+tarname+'extends'+target['extends']+'\n'
    if 'objects' in keys and target['objects'] is not '':
            for key in target['objects'].keys():
                    if key in list_obj:
                            err_str+='Error 07:Redundant definition of object '+key+'!\n'
                    else:
                            list_obj.append(key)
                    valstr=val_root(key,target['objects'][key],False)
                    err_str+=valstr[0]
                    war_str+=valstr[1]
    if 'relations' in keys and target['relations'] is not '' and isroot:
            for key in target['relations'].keys():
                if key in list_rel:
                        err_str+='Error 07:Redundant definition of relation '+key+'!\n'
                else:
                        list_rel.append(key)
                if 'nature' not in target['relations'][key]:
                        err_str+='Error01: the field [nature] is not defined in root[relations]'+key+']\n'
                elif target['relations'][key]['nature'] is not 'relation':
                        err_str+='Error 05:the nature of'+tarname+'[relations]['+key+'] is not correct!\n'
                if 'from' not in target['relations'][key]:
                        err_str+='Error01: the field [from] is not defined in'+tarname+'[relations]['+key+']\n'
                if 'to' not in target['relations'][key]:
                        err_str+='Error01: the field [to] is not defined in'+tarname+'[relations]['+key+']\n'
                if 'directional' not in target['relations'][key]:
                        err_str+='Error01: the field [directional] is not defined in'+tarname+'[relations]['+key+']\n'
    if 'library' in keys and not isroot:
        war_str+='Warning 02:Detect of a library member in'+tarname+',but '+tarname+' is not the root object\n'
    return err_str,war_str,list_obj,list_rel
                    
#prints the model in screen
def printModel():
    print ("Model")
    #print model.toStr("")

#print parse("Bank.rau")
#root Object
model = parse("Bank.rau")
#printModel()
#print model.toJson("")

#print Object.objects
#print Object.relations
#print model["objects"]

    
