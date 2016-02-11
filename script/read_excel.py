import os
import xlrd
import openpyxl

# read excel
top_path = "/Users/brian/Desktop/pillars of eternity/pillars-of-eternity-translation-xmls"

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
            for rowx in range(1, sheet.nrows):
                values = sheet.row_values(rowx)
                key = values[0].split()[0]
                #print key
                full_table.append(values)
                full_dict[key].append(values)

# read translated result
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

            full_translated_table.append((name, id, default_text, female_text,full_filename))


# try to match translated result with in excel
print("=========== try to match")
for translated in full_translated_table:
    table = translated[0]
    if table not in full_dict:
        print(table, translated[-1])

    values_list = full_dict[table]
    id = translated[1]
    for values in values_list:
        if values[1] == id:
            break
    else:
        print(table, id, translated[-1])



# wb = openpyxl.Workbook()
# ws = wb.active
#
# for values in full_table:
#     ws.append(values)
#
# wb.save("full_table.xlsx")

print("done")
