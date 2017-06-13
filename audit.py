#This code is part of the final project

import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

# This pattern finds different types of streets in street names
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

# The list of street types that we want to have
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

# The list of dictionaries, containing street types that need to be changed to match the 'expected' list
mapping = { "St": "Street", "St.": "Street", "street": "Street",
            "Ave": "Avenue", "Ave.": "Avenue", "AVE": "Avenue,", "avenue": "Avenue",
            "Rd.": "Road", "Rd": "Road", "road": "Road",
            "Blvd": "Boulevard", "Blvd.": "Boulevard", "Blvd,": "Boulevard", "boulevard": "Boulevard",
            "broadway": "Broadway",
            "square": "Square", "square": "Square", "Sq": "Square",
            "way": "Way",
            "Dr.": "Drive", "Dr": "Drive",
            "ct": "Court", "Ct": "Court", "court": "Court",
            "cres": "Crescent", "Cres": "Crescent", "Ctr": "Center",
            "Hwy": "Highway", "hwy": "Highway",
            "Ln": "Lane", "Ln.": "Lane",
            "parkway": "Parkway" }

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type].add(street_name)

def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit_name(osmfile):
    osm_file = open(osmfile, "r")
    street_types = defaultdict(set)
    
    # Iteratively parses the XML file
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        # Iterates through the 'tag' tag of node and way tags
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

def update_name(name, mapping):
    output = list()
    parts = name.split(" ")
    for part in parts:
        if part in mapping:
            output.append(mapping[part])
        else:
            output.append(part)
    return " ".join(output)  
                       
def dicti(data, item):
    data[item] += 1

def get_postcode(elem):
    return (elem.attrib['k'] == "addr:postcode")

def audit_postcode(osmfile):
    osm_file = open(osmfile, "r")
    data = defaultdict(int)
    # Parsing the XML file
    for event, elem in ET.iterparse(osm_file, events=("start",)):
        
        # Iterating through node and way elements.
        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if get_postcode(tag):
                    dicti(data, tag.attrib['v'])
    return data

def update_postcode(digit):
    output = list()
    
    first_category = re.compile('^\D*(\d{5}$)', re.IGNORECASE)
    second_category = re.compile('^(\d{5})-\d{4}$')
    third_category = re.compile('^\d{6}$')
    
    # For postcodes that are 5-digit long or are in this format 'CA 12345'
    if re.search(first_category, digit):
        new_digit = re.search(first_category, digit).group(1)
        output.append(new_digit)
    
    # For postcodes that are in this format '12345-6789'
    elif re.search(second_category, digit):
        new_digit = re.search(second_category, digit).group(1)
        output.append(new_digit)
    
    # For postcodes that are 6-digit long
    elif re.search(third_category, digit):
        third_output = third_category.search(digit)
        new_digit = '00000'
        output.append('00000')
    
    # For postcodes equal to 'CA' or shorter than 5-digit long
    elif digit == 'CA' or len(digit) < 5:
        new_digit = '00000'
        output.append(new_digit)

    return ', '.join(str(x) for x in output) 



