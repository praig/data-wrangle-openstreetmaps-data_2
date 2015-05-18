'''
Created on May 2, 2015

@author: PR0562
'''
import xml.etree.ElementTree as ET
import pprint
import re

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')


def key_type(element, keys,tags):
    if element.tag == "tag":
        if element.attrib['k'] in tags.keys():
            tags[element.attrib['k']]+=1
        else:
            tags[element.attrib['k']]=1
        if (lower.search(element.attrib['k'])):
            keys['lower']+=1 
            return keys
        if (lower_colon.search(element.attrib['k'])):
            keys['lower_colon']+=1 
            return keys
        if (problemchars.search(element.attrib['k'])):
            keys['problemchars']+=1 
            return keys
        keys['other']+=1
        
    return keys



def process_map(filename):
    keys = {"lower": 0, "lower_colon": 0, "problemchars": 0, "other": 0}
    tags={}
    for _, element in ET.iterparse(filename):
        keys = key_type(element, keys,tags)

    return keys,tags

if __name__ == "__main__":
    keys,tags = process_map('..\Miami.xml')
    pprint.pprint(keys)
    pprint.pprint(tags)
    
