# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import xlrd
import openpyxl

HOME_DIR = u"/Users/brian/Desktop/pillars of eternity"
OUTPUT_DIR = u"output"
TEMP_DIR = u"temp_output"
ORIGINAL_EXCEL_DIR = u"poe_original_excel/pillars-of-eternity-translation-xmls"
TRANSLATE_GROUP_RESULT = u"translate_group_result"


COL_INDEX = u"index"

TAG_STRING_TABLE_ENTRY = u"Entry"
TAG_STRING_TABLE_NAME = u'Name'
TAG_STRING_TABLE_ID = u'ID'
TAG_STRING_TABLE_DEFAULT_TEXT = u"DefaultText"
TAG_STRING_TABLE_FEMALE_TEXT = u"FemaleText"

# read translated result from each group
translated_result_list = [
    {
        u"group_name": u"3dm5.0",
        u"path": u"3dm_5.0",
    },
    {
        u"group_name": u"ali3.5",
        u"path": u"cn_ali_3.5",
    },
    {
        u"group_name": u"3dm4.0+ali1.5",
        u"path": u"3DMv4.0+ALI213v1.5-Pillars.of.Eternity.CHT.v1.6",
    },
    {
    u"group_name": u"cht_1.06",
    u"path": u"2015-07-07_Pillars of Eternity_CHT_v1.0_(For 1.06.0617)",
    },
    {
    u"group_name": u"1.5v2",
    u"path": u"汉化版1.5正式版2",
    },
    {
    u"group_name": u"tw",
    u"path": u"tw",
    },
]

#data = np.zeros((2,), dtype=[('A', 'i4'),('B', 'f4'),('C', 'a10')])

translated_df_list = []

for result in translated_result_list:
    translated_query_list = []

    group_name = result[u"group_name"]
    path = os.path.join(HOME_DIR, TRANSLATE_GROUP_RESULT, result[u"path"])
    print(group_name, path)

    default_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                            col_tilte = TAG_STRING_TABLE_DEFAULT_TEXT)

    female_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                            col_tilte = TAG_STRING_TABLE_FEMALE_TEXT)


    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            if filename.startswith(("~", ".")):
                continue
            full_filename = os.path.join(HOME_DIR, dirpath, filename)
            #print full_filename.encode('utf-8')

            # parse string table xml
            tree = ET.parse(full_filename)
            root = tree.getroot()

            name = root.find(TAG_STRING_TABLE_NAME).text
            #print name.encode('utf-8')

            for entry in root.iter(TAG_STRING_TABLE_ENTRY):
                id = entry.find(TAG_STRING_TABLE_ID).text
                default_text = entry.find(TAG_STRING_TABLE_DEFAULT_TEXT).text
                female_text = entry.find(TAG_STRING_TABLE_FEMALE_TEXT).text

                item = {}
                item[u"index"] = u"{name}_{id}".format(name = name, id = id)
                item[default_text_key] = default_text
                item[female_text_key] = female_text

                #print item
                translated_query_list.append(item)

    translated_df = pd.DataFrame(translated_query_list)
    translated_df = translated_df.set_index(COL_INDEX)
    #print(translated_df.head())
    print translated_df.describe()
    translated_df_list.append(translated_df)

translated_df_merge_result = translated_df_list[0]
#print u"Left-->"
#print translated_df_merge_result.describe()

for df in translated_df_list[1:]:
    #print u"Right-->"
    #print df.describe()
    #translated_df_merge_result = pd.concat([result, df], axis=1)
    translated_df_merge_result = translated_df_merge_result.join(df, how='outer')
    #print u"translated_df_merge_result-->"
    #print translated_df_merge_result.describe()
#translated_df_merge_result = pd.concat(translated_df_list[0:1], axis=1)
print translated_df_merge_result.head()
if u"conversations\00_dyrwood\00_bs_celby_1" in translated_df_merge_result:
    print u"has key"
    print translated_df_merge_result.describe()


# output merge result to excel
merge_result_output_filename = os.path.join(HOME_DIR, TEMP_DIR, u'merge_result.xlsx')
translated_df_merge_result.to_excel(merge_result_output_filename)

original_excel_path = os.path.join(HOME_DIR, ORIGINAL_EXCEL_DIR)

# for dirpath, dirnames, filenames in os.walk(original_excel_path):
#     for filename in filenames:
#         if filename.startswith(("~", ".")):
#             continue
#
#         full_filename = os.path.join(HOME_DIR, dirpath, filename)
#         #print full_filename
#
#         df = pd.read_excel(full_filename)
#         print(df.head())
#
#         #df[u'index'] = df[u'Table'] + u'_' + df[u'ID']
#         df.set_index(u'index')
#         print df.describe()
#
#         break

for dirpath, dirnames, filenames in os.walk(original_excel_path):
    for filename in filenames:
        if filename.startswith(("~", ".")):
            continue

        full_filename = os.path.join(dirpath, filename)
        output_full_filename = os.path.join(OUTPUT_DIR, u"new_"+filename)
        #print full_filename
        full_table = []
        book = xlrd.open_workbook(full_filename)

        wb = openpyxl.Workbook()
        ws = wb.active

        for sheet in book.sheets():
            for rowx in range(0, sheet.nrows):
                # Table	ID	Speaker	Listener	English	English Female	Mod	Mod Female	Revision
                table, id, speaker, listener, english, english_female, mod, mod_female, revision = sheet.row_values(rowx)
                if rowx > 0:

                    key = u"{table}_{id}".format(table = table.split()[0], id = id)
                    # print key
                    if key not in translated_df_merge_result.index:
                        mod = english
                        mod_female = english_female

                    else:
                        #print key
                        translated_result = translated_df_merge_result.ix[key]

                        #print(translated_df_merge_result.loc[key,u'[3dm5.0]DefaultText'].encode('utf-8'))
                        # for value in translated_df_merge_result.loc[key]:
                        #     if value:
                        #         print value.encode('utf-8')

                        for result in translated_result_list:
                            group_name = result[u"group_name"]
                            default_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                                                    col_tilte = TAG_STRING_TABLE_DEFAULT_TEXT)

                            female_text_key = u"[{group_name}]{col_tilte}".format(group_name = group_name,
                                                                                    col_tilte = TAG_STRING_TABLE_FEMALE_TEXT)

                            default = translated_result[default_text_key]
                            try:
                                if default:
                                    mod = default
                                    mod_female = translated_result[female_text_key]

                                    #print default
                                    break
                            except:
                                print u"\n======"

                                print u"key: ", default_text_key
                                print u"text: ", default
                                print "Unexpected error:", sys.exc_info()[0]
                                mod = default[1]
                                mod_female = translated_result[female_text_key][0]
                            else:
                                # mod = english
                                # mod_female = english_female
                                pass

                ws.append((table, id, speaker, listener, english, english_female, mod, mod_female, revision))
        print(u"{filename} outputed").format(filename = output_full_filename)
        wb.save(output_full_filename)
