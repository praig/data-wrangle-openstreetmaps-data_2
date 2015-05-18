'''
Created on May 2, 2015

@author: PR0562
'''
import xml.etree.ElementTree as ET
import pprint
def count_tags(filename):
    d={}    
    tree = ET.parse(filename)
    root = tree.getroot()
    d[root.tag]=1
    d=peter(d,root)    
    return d
def peter(d,o):
    for child in o:
        if (d.has_key(child.tag)):
            d[child.tag]+=1
        else:
            d[child.tag]=1
        d=peter(d,child)    
    return d
if __name__ == "__main__":
    tags = count_tags('..\Miami.xml')
    pprint.pprint(tags)