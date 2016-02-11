import os

top_path = "/Users/brian/Desktop/pillars of eternity/3DMv4.0+ALI213v1.5-Pillars.of.Eternity.CHT.v1.6"
#top_path = "/Users/brian/Desktop/pillars of eternity/tw"

import xml.etree.ElementTree as ET

full_translated_table = []

for dirpath, dirnames, filenames in os.walk(top_path):
    for filename in filenames:
        if filename.startswith(("~", ".")):
            continue
        full_filename = os.path.join(dirpath, filename)
        #print full_filename

        tree = ET.parse(full_filename)
        root = tree.getroot()

        # print root.tag, root.attrib

        # for child in root:
        #     print child.tag, child.attrib

        # for entry in root.iter('Entries'):
        #     print entry.tag, entry.attrib
        name = root.find('Name').text

        for entry in root.iter('Entry'):
            id = entry.find('ID').text
            default_text = entry.find('DefaultText').text
            female_text = entry.find('FemaleText').text
            #print(id, default_text, female_text)

            full_translated_table.append((name, id, default_text, female_text))
