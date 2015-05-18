'''
Created on May 8, 2015

@author: PR0562
'''
import xml.etree.ElementTree as ET
import pprint
import re

def get_db(databasename):
    # For local use
    from pymongo import MongoClient
    client = MongoClient()
    db = client[databasename]
    return db

def parse_tree(filename):
    tree= ET.parse(open(filename,"r"))
    return tree.getroot()

def import_data(treeroot,db):
    # loop through the data
    for child in treeroot:
        cleaned_data=clean_data(child)
        if cleaned_data != None:
            db.miami.insert(cleaned_data)
        
def clean_data(element):
    datum={
            "created": {} #this dictionary will always be present
           }
    created_keys=set(['version','changeset','timestamp','user','uid'])
    pos_keys=set(["latitudude","longitude","lon","lat"])
    suite_flag=None #set to indicate a suite needs to be added
 
    # prep work done, get the attributes for the main element 
    if element.tag == "node" or element.tag == "way" :
        datum['type']=element.tag
        keys=element.attrib.keys()
        for key in keys:
            if key in created_keys:
                datum["created"][key]= element.attrib[key]
            elif key in pos_keys:
                pass #I do not want to add unless I have both lon and lat
            else:
                datum[key]=element.attrib[key]
        
        #don't add unless both keys are present        
        if 'lat' in keys and 'lon' in keys:
            datum["pos"]=[float(element.attrib['lat']),float(element.attrib['lon'])]
        
        #process second level tags
        for child in element:
            if child.tag=="tag" and child.attrib['k'].startswith("addr") and child.attrib['k'].count(":")==1:
                if 'address' not in datum.keys():  #not all elements have address info so the dict only added when needed
                    datum['address']={}
                suite_flag=clean_address(child,suite_flag)
                datum['address'][child.attrib['k'].replace('addr:','')]=child.attrib['v']
            elif child.tag=="nd":
                if 'node_refs' not in datum.keys(): #not all elements have node_refs info so the list only added when needed
                    datum['node_refs']=[]
                datum['node_refs'].append(child.attrib['ref'])
            else:
                datum[child.attrib['k']] = child.attrib['v']   
            if suite_flag:
                datum['address']['suite']=suite_flag
    else:
        # not a node or a way. return nothing
        return None
    return datum

def clean_address(tag,suite_flag):
    if tag.attrib['k'] == "addr:street":
        return clean_street(tag,suite_flag)
    if tag.attrib['k'] == "addr:postcode":
        return clean_postcode(tag,suite_flag)
 
def clean_postcode(tag,suite_flag):
    tag.attrib['v']=re.sub("FL ?-?","",tag.attrib['v'])[:5] 
    if len(tag.attrib['v'])!=5:
        tag.attrib['v']=None
                
    return suite_flag
  
def clean_street(tag,suite_flag):
    #valid street types        
    expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road","Plaza", 
            "Trail", "Parkway", "Commons", "Terrace","Way","Path","Highway","Circle","Causeway","Highway"]
    #abbreviations to clean up
    mapping = { "St": "Street",
            "St.": "Street",
            "ave":"Avenue",
            "Ave":"Avenue",
            "Ave.":"Avenue",
            "Blvd":"Boulevard",
            "Cirlce":"Circle", #clean up misspelling
            "Ct":"Court",
            "Dr":"Drive",
            "Hwy":"Highway",
            "Rd":"Road",
            "Rd.":"Road",
            "St":"Street",
            "St.":"Street"
            }
    #look for suite/apt tags
    s= re.compile(r',?\s(Suite)?\s?#?\d*?$', re.IGNORECASE).search(tag.attrib['v'])
    if s:
        tag.attrib['v']=re.sub(s.group()+"$","",tag.attrib['v'])
        suite_flag=re.sub(",\s*","",s.group())
    
    # cleanup potential abbreviations
    for key in mapping.keys():
        tag.attrib['v']= re.sub(key+"$",mapping[key],tag.attrib['v'])
        
    #test for street name existence   
    m = re.compile(r'\b\S+\.?$', ).search(tag.attrib['v'])
    
    #found a name    
    if m:
        street_type = m.group()
        if street_type not in expected:
            print "Parsing Error: Unexpected street type found: ",street_type," Expanded street address: ",tag.attrib['v']
            tag.attrib['v']=None #name is no good. drop it
            
    return suite_flag

if __name__ == "__main__":
    db=get_db("udacity")
    treeroot=parse_tree("..\Miami.xml")
    import_data(treeroot,db)
    print db.collection_names()