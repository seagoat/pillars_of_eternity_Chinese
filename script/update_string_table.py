# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import xlrd
import openpyxl

HOME_DIR = u"/Users/brian/Documents/workplace/pillars_of_eternity_Chinese"
ORIGINAL_STRINGTABLE_DIR = u"string-table"
OUTPUT_DIR = u"output"


TEMP_DIR = u"temp_output"
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
        u"group_name": u"3dm4.0+ali1.5",
        u"path": u"3DMv4.0+ALI213v1.5-Pillars.of.Eternity.CHT.v1.6",
    },
    {
        u"group_name": u"ali3.5",
        u"path": u"cn_ali_3.5",
    },
    {
        u"group_name": u"3dm5.0",
        u"path": u"3dm_5.0",
    },
    # {
    # u"group_name": u"cht_1.06",
    # u"path": u"2015-07-07_Pillars of Eternity_CHT_v1.0_(For 1.06.0617)",
    # },
    # {
    # u"group_name": u"1.5v2",
    # u"path": u"汉化版1.5正式版2",
    # },
    # {
    # u"group_name": u"tw",
    # u"path": u"tw",
    # },
]

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
            full_filename = os.path.join(dirpath, filename)
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

translated_df_merge_result.fillna(value="")


en_strtbl_path = os.path.join(HOME_DIR, ORIGINAL_STRINGTABLE_DIR)
output_strtbl_path = os.path.join(HOME_DIR, OUTPUT_DIR)

for dirpath, dirnames, filenames in os.walk(en_strtbl_path):
    for filename in filenames:
        if filename.startswith(("~", ".")):
            continue
        if not filename.endswith(("stringtable")):
            continue

        #old english string table file
        src_filename = os.path.join(dirpath, filename)
        # output to new filename
        dst_path = dirpath.replace(en_strtbl_path, output_strtbl_path)
        dst_filename = src_filename.replace(en_strtbl_path,output_strtbl_path)


        # parse string table xml
        tree = ET.parse(src_filename)

        root = tree.getroot()

        name = root.find(TAG_STRING_TABLE_NAME).text

        for entry in root.iter(TAG_STRING_TABLE_ENTRY):
            id = entry.find(TAG_STRING_TABLE_ID).text
            default_text_item = entry.find(TAG_STRING_TABLE_DEFAULT_TEXT)
            female_text_item = entry.find(TAG_STRING_TABLE_FEMALE_TEXT)

            key = u"{name}_{id}".format(name = name, id = id)
            # print key
            if key not in translated_df_merge_result.index:
                continue
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
                            if u"nan" == unicode(default):
                                continue
                            default_text_item.text = unicode(default)
                            #if default_text_item.
                            female_text_item_text = translated_result[female_text_key]
                            if female_text_item_text:
                                female_text_item.text = unicode(female_text_item_text)

                            #print default
                            break
                    except:
                        if default[1]:
                            if u"nan" == unicode(default[1]):
                                continue
                            default_text_item.text = unicode(default[1])
                            if not translated_result[female_text_key].empty:
                                female_text_item_text = translated_result[female_text_key][0]
                                if female_text_item_text:
                                    female_text_item.text = unicode(female_text_item_text)
                    else:
                        # mod = english
                        # mod_female = english_female
                        break




        #output
        try:
            os.makedirs(dst_path)
        except:
            pass

        try:
            tree.write(dst_filename, encoding="utf-8")
        except Exception as e:
            print src_filename
            print e
            print tree
