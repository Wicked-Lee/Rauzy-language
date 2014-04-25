import json
import os
import pprint
from Relation import Relation
from collections import defaultdict


class Object(object):
    model = False
    comp = False
    folder = ""
    #library of all objects dictionary key = object name , value = Object
    objects = dict()
    #library of relations dictionary key = relation name , value = relation value
    relations = dict()
    #library with only the referenced objects
    objectsLib = dict()
    #library with only the referenced relations
    relationsLib = dict()
    #library of all objects dictionary key = object name , value = Object
    objects2 = dict()
    #library of relations dictionary key = relation name , value = relation value
    relations2 = dict()
    #library with only the referenced objects
    objectsLib2 = dict()
    #library with only the referenced relations
    relationsLib2 = dict()

    #dict of objects to be flattened
    flatObj = dict()
    #dict of relations to be flattened
    flatRel = dict()
    #dict of objects to be flattened
    flatObj2 = dict()
    #dict of relations to be flattened
    flatRel2 = dict()

    @staticmethod
    def dupe_checking_hook(pairs):
        result = dict()
        for key, val in pairs:
            if key in result:
                print 'Error 07:Redundant definition of ' + key + '!\n'
            #Here I can give result a field
            #"Error 07":"Redundant definition of "+key+ "!\n"
            result[key] = val
        return result

    #finds the Object with the given name
    #handle "Error 03: the object xx is not defined !"
    @staticmethod
    def findObject(name):
        if not Object.comp:
            if name in Object.objects.keys():
                return Object.objects[name]
        else:
            if name in Object.objects2.keys():
                return Object.objects2[name]

    #finds the relation with the given name
    #handle "Error 04:the relation xx is not defined !"
    @staticmethod
    def findRelation(name):
        if not Object.comp:
            if name in Object.relations.keys():
                return Object.relations[name]
        else:
            if name in Object.relations2.keys():
                return Object.relations2[name]

    @staticmethod
    def findLibObject(name):
        if name in Object.objectsLib.keys():
            return Object.objectsLib[name]

    @staticmethod
    def findLibRelation(name):
        if name in Object.relationsLib.keys():
            return Object.relationsLib[name]

    @staticmethod
    def addObject(name, obj):
        if not Object.comp:
            Object.objects[name] = obj
        else:
            Object.objects2[name] = obj

    @staticmethod
    def addRelation(name, value):
        if not Object.comp:
            Object.relations[name] = value
        else:
            Object.relations2[name] = value

    #handle "Error 02:the library file xx is not found!"
    @staticmethod
    def readLibrary(fl):
        err_str = ''
        war_str = ''
        list_obj = []
        list_rel = []
        ext_obj = []
        ext_rel = []
        dict_ft = defaultdict(list)
        try:
            with open(Object.folder + fl) as f:
                #with object_pairs_hook method, we can check "Error 07" at the same level
                target = json.loads(f.read(), object_pairs_hook=Object.dupe_checking_hook)
            reldict = defaultdict(list)
            err_str, war_str = Object.val_lib(fl, target, target, True, list_obj,
                                              list_rel, reldict, ext_obj, ext_rel, dict_ft)
            #pprint.pprint(reldict)
            #print('\n'*2)
            err_str += Object.cycle_test(reldict, [], '', True)
            err_str += Object.notdefined(list_obj, list_rel, ext_obj, ext_rel, dict_ft)
            if not err_str:
                for key in target.keys():
                    if key == "objects":
                        for objectName in target[key].keys():
                            #We add all the objects contained in "objectName" into global dictionary "Object.
                            #objects" and their name into local "objects" list to give a tree structure
                            obj = Object(objectName, target[key][objectName])
                            #add object into Object.objects
                            Object.addObject(objectName, obj)
                            #add object into Object.objectsLib
                            if not Object.comp:
                                Object.objectsLib[objectName] = obj
                            else:
                                Object.objectsLib2[objectName] = obj
                    elif key == "relations":
                        for relationName in target[key].keys():
                            relation = Relation(relationName, target[key][relationName])
                            Relation.addRelation(relationName, relation)
                            Object.addRelation(relationName, relation)
                            if not Object.comp:
                                Object.relationsLib[relationName] = relation
                            else:
                                Object.relationsLib2[relationName] = relation
        except IOError:
            err_str += 'Error 02: library file is not found!\n'
            list_obj = ['Error 02']
        return [err_str, war_str, list_obj, list_rel]

    ##handle "Error 03: the object xx is not defined !"
    ##handle "Error 04:the relation xx is not defined !"
    @staticmethod
    def notdefined(list_obj, list_rel, ext_obj, ext_rel, dict_ft):
        err_str = ''
        if ext_obj is not []:
            for obj in ext_obj:
                if obj not in list_obj:
                    err_str += 'Error 03: the object ' + obj + ' extended in the lib is not defined !\n'
        if ext_rel is not []:
            for rel in ext_rel:
                if rel not in list_rel:
                    err_str += 'Error 04:the relation ' + rel + ' extended in the lib is not defined !\n'
        if dict_ft is not {}:
            for key in dict_ft.keys():
                if key not in list_obj and type(dict_ft[key]) == list and dict_ft[key]:
                    for tarname in dict_ft[key]:
                        err_str += 'Error 03: the object ' + key
                        err_str += ' in ' + tarname + ' is not defined !\n'
        return err_str

    #handle "Error 06:A cyclic dependency detected! The cycle is
    #"xx0-(include/extends)->xx1-(include/extends)->xx2-(include/extends)->..-(include/extends)->xx0"
    @staticmethod
    def cycle_test(ct, tr, node, isroot):
        err_str = ''
        if isroot:
            for key in ct.keys():
                tr = []
                tr.append(key)
                err_str += Object.cycle_test(ct, tr, key, False)
        elif node in ct.keys() and ct[node]:
            for i in ct[node]:
                if i in tr:
                    tr.append(i)
                    temp = 'Error 06:A cyclic dependency detected! The cycle is '
                    temp += '-(include/extends)->'.join(tr) + '\n'
                    tr.remove(i)
                    return temp
                else:
                    tr.append(i)
                    err_str += Object.cycle_test(ct, tr, i, False)
                    if i in tr:
                        tr.remove(i)
        else:
            tr.remove(node)
        return err_str

    #handle "Error 00: Json type xx expected in xx!"
    #The rule is that following keys are defined keywords:
    #'nature', 'objects','relations','properties','library',
    #'extends','from','to','directional'
    @staticmethod
    def val_type(tarname, target):
        err_str = ''
        #[nature] must be string
        if 'nature' in target and not isinstance(target['nature'], unicode):
            print type(target['nature'])
            err_str += 'Error 00: Json type "string" expected in' + tarname + '[nature]! \n'
        #[objects] must be dict of dicts
        if 'objects' in target:
            if isinstance(target['objects'], dict):
                for key in target['objects'].keys():
                    if not isinstance(key, unicode):
                        err_str += 'Error 00: Jason type "string" expected in the left value of '
                        err_str += tarname + ' [objects][' + key + ']! \n'
                    if not isinstance(target['objects'][key], dict):
                        err_str += 'Error 00: Jason type "object" expected in the right value of '
                        err_str += tarname + '[objects][' + key + ']! \n'
            else:
                err_str += 'Error 00: Jason type "object" expected in' + tarname + '[objects]! \n'
        #[relations] must be dict of dicts
        if 'relations' in target:
            if isinstance(target['relations'], dict):
                for key in target['relations'].keys():
                    if not isinstance(key, unicode):
                        err_str += 'Error 00: Jason type "string" expected in the left value of '
                        err_str += tarname + ' [relations][' + key + ']! \n'
                    if not isinstance(target['relations'][key], dict):
                        err_str += 'Error 00: Jason type "object" expected in the right value of '
                        err_str += tarname + '[relations][' + key + ']! \n'
            else:
                err_str += 'Error 00: Jason type "object" expected in' + tarname + '[relations]! \n'
        #[extends] must be string
        if 'extends' in target and not isinstance(target['extends'], unicode):
            err_str += 'Error 00: Jason type "string" expected in' + tarname + '[extends]! \n'
        #[properties] must be dict of string keys
        if 'properties' in target:
            if isinstance(target['properties'], dict):
                    for key in target['properties'].keys():
                        if not isinstance(key, unicode):
                            err_str += 'Error 00: Jason type "string" expected in the left value of '
                            err_str += tarname + ' [properties][' + key + ']! \n'
            else:
                err_str += 'Error 00: Jason type "object" expected in' + tarname + '[properties]! \n'
        #[library] must be string
        if 'library' in target and not isinstance(target['library'], unicode):
            err_str += 'Error 00: Jason type "str" expected in' + tarname + '[library]! \n'
        #[from] must be list of strings
        if 'from' in target:
            if isinstance(target['from'], list):
                    for element in target['from']:
                        if not isinstance(element, unicode):
                            err_str += 'Error 00: Jason type "string" expected in '
                            err_str += tarname + ' [from][' + element + ']! \n'
            else:
                print type(target['from'])
                err_str += 'Error 00: Jason type "array" expected in' + tarname + '[from]! \n'
        #[to] must be list of strings
        if 'to' in target:
            if isinstance(target['to'], list):
                    for element in target['to']:
                        if not isinstance(element, unicode):
                            err_str += 'Error 00: Jason type "string" expected in '
                            err_str += tarname + ' [to][' + element + ']! \n'
            else:
                err_str += 'Error 00: Jason type "array" expected in'
                err_str += tarname + '[to]! \n'
        if 'directional' in target:
            if not isinstance(target['directional'], bool):
                err_str += 'Error 00: Jason type "bool" expected in'
                err_str += tarname + '[directional]! \n'
        return err_str, bool(err_str)

    #handle "Error 01: xx in the xx not defined!"
    #handle "Error 03:the object xx is not defined !"
    #handle "Error 04:the relation xx is not defined !"
    #handle "Error 05:the nature of xx is not correct!"
    #handle "Error 07:Redundant definition of xx!"
    #handle "Error 08:Incorrect library file format:(xx not recognized)!"
    #handle "Warning 01:xx should not be defined in a libray relation."
    #handle "Warning 03: 'objects' and 'relations' in object A
    #will be overriden by these of object B as A extends B"
    @staticmethod
    def val_lib(tarname, lib, target, islib, list_obj,
                list_rel, rd, ext_obj, ext_rel, dict_ft):
        err_str = ""
        war_str = ""
        #Type checking
        Type1 = Object.val_type(tarname, target)
        if Type1[1]:
            err_str += Type1[0]
        else:
            if not islib:
                if 'extends' in target and target['extends']:
                    rd[tarname].append(target['extends'])
                    if target['extends'] not in ext_obj:
                        ext_obj.append(target['extends'])
                elif 'objects' in target and target['objects']:
                    for key in target['objects'].keys():
                        rd[tarname].append(key)
            if 'nature' not in target.keys() or not target['nature']:
                err_str += 'Error 01: the field [nature] is not defined in the library ' + tarname + '!\n'
            elif target["nature"] != "library" and islib:
                err_str += 'Error 05:the [nature] of library ' + tarname + ' is not correct!\n'
            elif target['nature'] != 'object' and not islib:
                err_str += 'Error 05:the [nature] of object ' + tarname + ' is not correct!\n'
            if 'extends' in target.keys() and target['extends']:
                if 'objects' in target.keys():
                    #target.pop("objects",None)
                    war_str += 'Warning 03: "objects" in object ' + tarname
                    war_str += ' will be overriden by these of object ' + target['extends']
                    war_str += ' as ' + tarname + 'extends' + target['extends'] + '\n'
                if 'relations' in target.keys():
                    #target.pop("relations",None)
                    war_str += 'Warning 03: "relations" in object ' + tarname
                    war_str += ' will be overriden by these of object ' + target['extends']
                    war_str += ' as ' + tarname + 'extends' + target['extends'] + '\n'
            if 'objects' in target.keys() and target['objects']:
                for key in target['objects'].keys():
                    #with below, we can check "Error 07" at the different levels
                    if key in list_obj:
                        err_str += 'Error 07:Redundant definition of object ' + key + '!\n'
                    else:
                        list_obj.append(key)
                    valstr = Object.val_lib(key, lib, target['objects'][key],
                                            False, list_obj, list_rel, rd,
                                            ext_obj, ext_rel, dict_ft)
                    err_str += valstr[0]
                    war_str += valstr[1]
            if islib and 'relations' in target and target['relations'] != {}:
                for key in target['relations'].keys():
                    #Type checking
                    Type2 = Object.val_type(tarname + '[relations][' + key + ']', target['relations'][key])
                    if Type2[1]:
                        err_str += Type2[0]
                    else:
                        if 'nature' not in target['relations'][key]:
                            err_str += 'Error 01: the field [nature] is not defined in '
                            err_str += tarname + '[relations][' + key + ']\n'
                        elif target['relations'][key]['nature'] != 'relation':
                            err_str += 'Error 05:the [nature] of' + tarname
                            err_str += '[relations][' + key + '] is not correct!\n'
                        if 'from' in target['relations'][key]:
                            war_str += 'Warning 01: the field [from] should not be defined in '
                            war_str += tarname + '[relations][' + key + ']\n'
                        if 'to' in target['relations'][key]:
                            war_str += 'Warning 01: the field [to] should not be defined in '
                            war_str += tarname + '[relations][' + key + ']\n'
                        if 'directional' not in target['relations'][key]:
                            print target['relations'][key]
                            err_str += 'Error 01: the field [directional] is not defined in '
                            err_str += tarname + '[relations][' + key + ']\n'
            if not islib and 'relations' in target and target['relations'] != {}:
                for key in target['relations'].keys():
                    #Type checking
                    Type3 = Object.val_type(tarname + '[relations][' + key + ']', target['relations'][key])
                    if Type3[1]:
                        err_str += Type3[0]
                    else:
                        if 'extends' in target['relations'][key] and target['relations'][key]['extends']:
                                string = target['relations'][key]['extends']
                                if string and string not in ext_rel:
                                    ext_rel.append(string)
                        #with below, we can check "Error 07" at the different levels
                        if key in list_rel:
                            err_str += 'Error 07:Redundant definition of relation ' + key + '!\n'
                        else:
                            list_rel.append(key)
                        if 'nature' not in target['relations'][key]:
                            err_str += 'Error 01: the field [nature] is not defined in lib['
                            err_str += tarname + '][relations][' + key + ']\n'
                        elif target['relations'][key]['nature'] != 'relation':
                            err_str += 'Error 05:the [nature] of' + tarname
                            err_str += '[relations][' + key + '] is not correct!\n'
                        if 'from' not in target['relations'][key] or target['relations'][key]['from'] == []:
                            err_str += 'Error 01: the field [from] is not defined in '
                            err_str += tarname + '[relations][' + key + ']\n'
                        else:
                            for obj in target['relations'][key]['from']:
                                dict_ft[obj].append(tarname + '[relations][' + key + '][from]')
                        if 'to' not in target['relations'][key] or target['relations'][key]['to'] == []:
                            err_str += 'Error 01: the field [to] is not defined in ' + tarname
                            err_str += '[relations][' + key + ']\n'
                        else:
                            for obj in target['relations'][key]['to']:
                                dict_ft[obj].append(tarname+'[relations]['+key+'][to]')
                        if 'extends' not in target['relations'][key] or target['relations'][key]['extends']:
                            if 'directional' not in target['relations'][key]:
                                err_str += 'Error 01: the field [directional] is not defined in '
                                err_str += tarname + '[relations][' + key + ']\n'
                        else:
                            try:
                                war_str += "Warning 03: [directional] in relation " + key
                                war_str += " will be overriden by that of relation "
                                war_str += target['relations'][key]['extends'] + " as "
                                war_str += key + " extends " + target['relations'][key]['extends'] + "\n"
                            except KeyError:
                                pass
            if islib:
                if 'relations' in target.keys() and target['relations']:
                    for key_rel in target['relations'].keys():
                        list_rel.append(key_rel)
                        if 'extends' in target['relations'][key_rel] and target['relations'][key_rel]['extends']:
                            string = target['relations'][key_rel]['extends']
                            if string and string not in ext_rel:
                                ext_rel.append(string)
                for key in target.keys():
                    if key not in ['nature', 'objects', 'relations']:
                        err_str += "Error 08:Incorrect library file format: ["
                        err_str += key + "] not recognized!\n"
            if 'library' in target.keys() and target['library']:
                war_str += 'Warning 02:Detect of a library member in ' + tarname
                war_str += ',but ' + tarname + ' is not the root object\n'
        return [err_str, war_str]

    #properties dictionary
    #objects list of strings
    #relations list of strings
    def __init__(self, name, parent, properties, objects, relations):
        self.name = name
        self.parent = parent
        self.properties = properties
        self.objects = objects
        self.relations = relations
        self.library = None

    def __init__(self, name, nested_json):
        self.name = name
        self.properties = dict()
        self.relations = []
        self.library = None
        if "library" in nested_json.keys():
            self.library = nested_json['library']
        if 'properties' in nested_json.keys():
            newProperties = nested_json["properties"]
            for prop in newProperties.keys():
                self.properties[prop] = newProperties[prop]
        #Object.objects is an array
        self.objects = []
        if 'extends' in nested_json.keys() and nested_json['extends']:
            self.parent = nested_json["extends"]
            par = Object.findObject(self.parent)
            self.inherit(par)
        else:
            self.parent = ""
            if 'objects' in nested_json.keys():
                for objName in nested_json['objects'].keys():
                    if nested_json['objects'][objName]:
                        #Construct "object" recursively
                        obj = Object(objName, nested_json['objects'][objName])
                        self.objects.append(objName)
                        if not Object.comp:
                            Object.objects[objName] = obj
                        else:
                            Object.objects2[objName] = obj
                    else:
                        with open(Object.folder+objName+".rau") as f:
                            target = json.loads(f.read())
                        obj = Object(objName, target)
                        self.objects.append(objName)
                        if not Object.comp:
                            Object.objects[objName] = obj
                        else:
                            Object.objects2[objName] = obj
            #relations must be an array
            if 'relations' in nested_json.keys():
                for rel in nested_json['relations']:
                    if not nested_json['relations'][rel]:
                        with open(Object.folder+rel+".rau") as f:
                            target = json.loads(f.read())
                        relation = Relation(rel, target)
                        self.objects.append(rel)
                        if not Object.comp:
                            Object.relations[rel] = relation
                        else:
                            Object.relations2[rel] = relation
                        self.relations.append(rel)
                    if isinstance(nested_json['relations'][rel], unicode):
                        self.relations.append(rel)
                    else:
                        relation = Relation(rel, nested_json['relations'][rel])
                        if not Object.comp:
                            Object.relations[rel] = relation
                        else:
                            Object.relations2[rel] = relation
                        self.relations.append(rel)

    def inherit(self, parent):
        if parent:
            self.objects = []
            self.relations = []
            if parent.properties:
                for prop in parent.properties:
                    if prop not in self.properties.keys():
                        self.properties[prop] = parent.properties[prop]
            if parent.objects:
                for obj in parent.objects:
                    self.objects.append(obj)
                #print(parent.objects)
            if parent.relations:
                for rel in parent.relations:
                    self.relations.append(rel)

    #return a raw string representation of the object
    def __str__(self):
        output = "Name : " + self.name + "\n"
        if self.parent:
            output += "Extends : " + self.parent + "\n"
        if self.properties:
            output += "Properties : \n"
            for prop in self.properties.keys():
                output += "\t" + prop + " : " + self.properties[prop] + "\n"
        if self.objects:
            output += "Objects : \n"
            output += "\t" + self.objects.__str__() + "\n"
        if self.relations:
            output += "Relations : \n"
            output += "\t" + self.relations.__str__() + "\n"
        if self.library:
            output += "Library :\n"
            output += "\t" + self.library + "\n"
        return output

    #return a string representation of the object
    def toStr(self, indent):
        #print('objects:'+self.name,self.parent)
        output = indent + "Name : " + self.name + "\n"
        if self.parent:
            output += indent + "Extends : " + self.parent + "\n"
        if self.properties:
            output += indent + "Properties : \n"
            for prop in self.properties.keys():
                output += indent + "\t" + prop + " : "
                output += self.properties[prop] + "\n"
        if self.objects:
            output += indent + "Objects : \n"
            for objName in self.objects:
                obj = Object.findObject(objName)
                output += obj.toStr(indent + "\t") + "\t"+indent
                output += "__________________________________\n"
        if self.relations:
            output += indent + "Relations : \n"
            for relName in self.relations:
                rel = Object.findRelation(relName)
                output += rel.toStr(indent + "\t") + "\t"+indent
                output += "__________________________________\n"
        return output

    #returns a string representation of this object
    #according to "func" indication
    def toStr2(self, indent, func):
        flat = False
        abstract = False
        level = 0
        level2 = 100
        if func == "flat":
            flat = True
        if func.startswith('abstract'):
            abstract = True
            if len(func.split()) == 2:
                level2 = int(func.split()[1])
                if level > level2:
                    abstract = False
                    return ''
        output = indent + "Name : " + self.name + "\n"
        if self.parent:
            output += indent + "Extends : " + self.parent + "\n"
        if self.properties:
            output += indent + "Properties : \n"
            for prop in self.properties.keys():
                output += indent + "\t" + prop + " : "
                output += self.properties[prop] + "\n"
        if self.objects and not flat:
            output += indent + "Objects : \n"
            for objName in self.objects:
                obj = Object.findObject(objName)
                if abstract:
                    func = 'abstract ' + str(level2-1)
                if obj:
                    output += obj.toStr2(indent + "\t", func) + "\t" + indent
                    output += "__________________________________\n"
        if self.relations and not flat and not abstract:
            output += indent + "Relations : \n"
            for relName in self.relations:
                rel = Object.findRelation(relName)
                output += rel.toStr(indent + "\t") + "\t" + indent
                output += "__________________________________\n"
        return output

    #returns a JSON representation of this object
    def toJson(self, indent):
        output = indent + "{\n"
        output += indent + "\"nature\" : " + "\"object\",\n"
        if self.library:
            output += indent + "\"library\" : " + "\"" + self.library + "\",\n"
        if self.parent:
            output += indent + "\"extends\" : \"" + self.parent + "\",\n"
        if not self.parent and self.objects:
            output += indent + "\"objects\" : " + indent + "{\n"
            for objName in self.objects:
                output += indent + "\t\"" + objName + "\" : "
                object = Object.findObject(objName)
                output += object.toJson(indent + "\t")
                output += ",\n"
            #erase last comma
            output = output[:-2] + "\n"
            output += indent + "},\n"
        if not self.parent and self.relations:
            output += indent + "\t\"relations\" : {\n"
            for rel in self.relations:
                relation = Object.findRelation(rel)
                output += relation.toJson(indent) + ",\n"
            #erase last comma
            output = output[:-2] + "\n"
            output += "\t},\n"
        if self.properties:
            output += indent + "\"properties\" : " + indent + "{\n"
            for prop in self.properties.keys():
                output += indent + "\t" + "\"" + prop + "\""
                output += " : \"" + self.properties[prop] + "\",\n"
            #erase last comma
            output = output[:-2] + "\n"
            output += indent + "}\n"
        else:
            #erase last comma
            output = output[:-2] + "\n"
        output += indent + "}"
        return output

#no need for that function this is done when reading
    @staticmethod
    def flatten(list_obj, list_rel):
        for obj in list_obj:
            temp = Object.findObject(obj)
            if temp.parent:
                if temp.objects:
                    for objName in temp.objects:
                        if objName not in list_obj:
                            list_obj.append(objName)
                if temp.relations:
                    for relName in temp.relations:
                        if relName not in list_rel:
                            list_rel.append(relName)
            if not Object.comp:
                Object.flatObj[obj] = temp
            else:
                Object.flatObj2[obj] = temp
        for rel in list_rel:
            if not Object.comp:
                Object.flatRel[rel] = Object.findRelation(rel)
            else:
                Object.flatRel2[rel] = Object.findRelation(rel)
