# -*- coding: utf-8 -*-

# read translated result
import os
from collections import defaultdict
import xml.etree.ElementTree as ET


top_path = "/Users/brian/Desktop/pillars of eternity/3DMv4.0+ALI213v1.5-Pillars.of.Eternity.CHT.v1.6"
#top_path = "/Users/brian/Desktop/pillars of eternity/tw"

translate_result = {
    u"3dm4.0+ali1.5":u"/Users/brian/Desktop/pillars of eternity/3DMv4.0+ALI213v1.5-Pillars.of.Eternity.CHT.v1.6",
    u"cht_1.06":u"/Users/brian/Desktop/pillars of eternity/2015-07-07_Pillars of Eternity_CHT_v1.0_(For 1.06.0617)",
    u"1.5v2":u"/Users/brian/Desktop/pillars of eternity/汉化版1.5正式版2",
    u"tw":u"/Users/brian/Desktop/pillars of eternity/tw",
}

full_translated_dict = defaultdict(list)

print("===Begin parse stringtables")

for group, path in translate_result.iteritems():
    print(group, path)

    top_path = path

    for dirpath, dirnames, filenames in os.walk(top_path):
        for filename in filenames:
            if filename.startswith(("~", ".")):
                continue
            full_filename = os.path.join(dirpath, filename)
            print full_filename.encode('utf-8')

            # parse string table xml
            tree = ET.parse(full_filename)
            root = tree.getroot()

            # print root.tag, root.attrib

            # for child in root:
            #     print child.tag, child.attrib

            # for entry in root.iter('Entries'):
            #     print entry.tag, entry.attrib
            name = root.find('Name').text
            print name.encode('utf-8')

            for entry in root.iter('Entry'):
                id = entry.find('ID').text
                default_text = entry.find('DefaultText').text
                female_text = entry.find('FemaleText').text
                #print(id, default_text, female_text)

                full_translated_dict[name].append([id, group, default_text, female_text])

print("===End parse stringtables")


print("===Begin read excel")
# try to read excel
# read excel
src_path = "/Users/brian/Desktop/pillars of eternity/pillars-of-eternity-translation-xmls"
dest_path = "/Users/brian/Desktop/pillars of eternity/output"
full_table = []

from collections import defaultdict
full_dict = defaultdict(list)

for dirpath, dirnames, filenames in os.walk(top_path):
    for filename in filenames:
        if filename.startswith(("~", ".")):
            continue

        full_filename = os.path.join(dirpath, filename)
        #print full_filename
        book = xlrd.open_workbook(full_filename)
        for sheet in book.sheets():
            for rowx in range(0, sheet.nrows):
                values = sheet.row_values(rowx)

                if rowx > 0:
                    name = values[0].split()[0]
                #print key
                full_dict[key].append(values)
                full_table.append(values)
