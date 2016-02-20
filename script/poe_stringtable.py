# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import xlrd
import openpyxl

TAG_STRING_TABLE_ENTRY = u"Entry"
TAG_STRING_TABLE_NAME = u'Name'
TAG_STRING_TABLE_ID = u'ID'
TAG_STRING_TABLE_DEFAULT_TEXT = u"DefaultText"
TAG_STRING_TABLE_FEMALE_TEXT = u"FemaleText"

class StringTable:
    def __init__(self):
        self.df = pd.DataFrame()

    def parse_file(self, filename):
        # parse string table xml
        tree = ET.parse(filename)
        root = tree.getroot()

        name = root.find(TAG_STRING_TABLE_NAME).text
        #print name.encode('utf-8')

        for entry in root.iter(TAG_STRING_TABLE_ENTRY):
            id = entry.find(TAG_STRING_TABLE_ID).text
            default_text = entry.find(TAG_STRING_TABLE_DEFAULT_TEXT).text
            female_text = entry.find(TAG_STRING_TABLE_FEMALE_TEXT).text

            print(name, id, default_text, female_text)

    def parse_dir(self, strtbl_dir):
        for dirpath, dirnames, filenames in os.walk(strtbl_dir):
            for filename in filenames:
                if filename.startswith(("~", ".")):
                    continue
                if not filename.endswith(("stringtable")):
                    continue
                full_filename = os.path.join(dirpath, filename)
                self.parse_file(full_filename)
