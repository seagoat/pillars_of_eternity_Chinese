# -*- coding: utf-8 -*-
"""永恒之柱汉化包处理工具(基于 python 3.0)

永恒之柱是一个游戏
目前没有官方中文,有很多的民间汉化包

但是有下面几个问题
1. 民间汉化包只有 windows 版本. 对于 Mac 和 Linux 来说,痛苦
2. 官方会更新,可能会追加新的文本.汉化包里面没有的话,就会显示为 Missing GUI
3. MAC 版本上,会显示省略号

本脚本的目的
1. 基于你主程序的的英文文本,添加汉化内容.没有汉化的部分,保留英文
1.1 因为楼上的原因,主程序如果更新过,可以自己更新汉化包,新追加的英文不会变成 Missing GUI 不需要等汉化组
2. 汉字之间追加空格,避免省略号(可选)
3. 可以选择优先使用哪个汉化包的内容

Example:

        $ python  main.py

详细的使用方法,等脚本完善之后再说

"""
import os
import xml.etree.ElementTree as ET
import pandas as pd

COL_INDEX = u"StringTableIndex"

TAG_STRING_TABLE_ENTRY = u"Entry"
TAG_STRING_TABLE_NAME = u'Name'
TAG_STRING_TABLE_ID = u'ID'
TAG_STRING_TABLE_DEFAULT_TEXT = u"DefaultText"
TAG_STRING_TABLE_FEMALE_TEXT = u"FemaleText"

def is_Chinese(char):
    return '\u4e00' <= char <= '\u9fff'

def all_Chinese(text):
    return all('\u4e00' <= char <= '\u9fff' for char in text)

def has_Chinese(text):
    return any('\u4e00' <= char <= '\u9fff' for char in text)

def is_ascii(text):
    """用来判断是否是普通英文符号."""
    return all(ord(c) < 128 for c in text)


def add_space(text):
    """用来在两个汉字之间添加空格"""

    # 存放拆分好的字符,有空格追加空格
    result = []

    for index in range(len(text)-1):
        first = text[index]
        second = text[index + 1]

        if (not is_ascii(first)) \
            and (first != u" ") \
            and (not is_ascii(second)) \
            and (second != u" "):
            # 连续两个中文字符，并且中间没有空格,在第一个字符后面追加空格
            result.append(first)
            result.append(u" ")
        else:
            result.append(first)
    # 追加最后一个不是空格的字符
    if text[-1] != ' ':
        result.append(text[-1])

    # 合并结果返回
    return u"".join(result)

def get_key_string(dirbase1, name, entry_id_text):
    # key = u"[{}]_[{}]".format(name, entry_id_text)
    key = u"[{}]_[{}]_[{}]".format(dirbase1, name, entry_id_text)
    # key = u"[{}]_[{}]_[{}]_[{}]".format(dirbase1, filename.lower(), name, entry_id_text)
    return key    

def parse_string_table_dir(path):
    """解析一个目录中所有的 string table 文件,返回一个 DataFrame 做为查询数据库"""
    print('Start parsing {}'.format(path))
    string_entry_list = []
    total_entry_id_count = 0
    translated_id_count = 0

    for dirpath, dirnames, filenames in os.walk(path):
        # data_expansion1/localized/en
        dirbase1_list = ('data_expansion1', 'data_expansion2', 'data')
        dirbase2 = 'localized'

        for dirbase1 in dirbase1_list:
            if dirbase1.lower() in dirpath.lower():
                break
        else:
            # 找不到就认为只有原版
            dirbase1 = 'data'
            # continue

        for filename in filenames:
            # 跳过各种奇怪的文件
            if filename.startswith(("~", ".")):
                continue
            if not filename.endswith(".stringtable"):
                continue

            # # debug
            # # print(filename)
            # if filename == '00_bs_celby.stringtable':
            #     find = True
            #     pass

            full_filename = os.path.join(dirpath, filename)

            # parse string table xml
            tree = ET.parse(full_filename)
            root = tree.getroot()

            name = root.find(TAG_STRING_TABLE_NAME).text

            for entry in root.iter(TAG_STRING_TABLE_ENTRY):
                entry_id = entry.find(TAG_STRING_TABLE_ID)

                if entry_id is None:
                    print('empty entry_id {} in file {}'.format(name, full_filename))
                    continue
                else:
                    entry_id_text = entry_id.text
                
                total_entry_id_count += 1

                default = entry.find(TAG_STRING_TABLE_DEFAULT_TEXT)
                if default is None:
                    default_text = ''
                else:
                    default_text = default.text

                female = entry.find(TAG_STRING_TABLE_FEMALE_TEXT)
                if female is None:
                    female_text = ''
                else:
                    female_text = female.text

                # 如果字符都是英文, 不采用
                if default_text and (not has_Chinese(default_text)):
                    # print('Skip English string: {}'.format(default_text))
                    default_text = ''
                else:
                    if default_text:
                        # print('Chinese string: {}'.format(default_text))
                        pass

                if female_text and (not has_Chinese(female_text)):
                    # print('Skip English string: {}'.format(female_text))
                    female_text = ''
                else:
                    if female_text:
                        # print('Chinese string: {}'.format(female_text))
                        pass
                    
                # 跳过全空的 entry
                if (not default_text) and (not female_text):
                    continue

                translated_id_count += 1
                
                item = {}
                # 用Entry 字段内容和 ID 组成 Index, 做为 string 的索引
                key = get_key_string(dirbase1, name, entry_id_text)
                # key = u"[{}]_[{}]_[{}]_[{}]".format(dirbase1, filename.lower(), name, entry_id_text)
                item[COL_INDEX] = key
                item[TAG_STRING_TABLE_DEFAULT_TEXT] = default_text
                item[TAG_STRING_TABLE_FEMALE_TEXT] = female_text

                # for previous_item in string_entry_list:
                #     if previous_item[COL_INDEX] == key:
                #         print(key)
                #         continue
                string_entry_list.append(item)

    string_entry_df = pd.DataFrame(string_entry_list)
    string_entry_df = string_entry_df.set_index(COL_INDEX)
    print(string_entry_df.describe())

    print('Get {} Chinese id from total {}'.format(translated_id_count, total_entry_id_count))
    return string_entry_df

def translate(game_path, output_path, translate_df, base_lan='en', need_add_space = True):
    """解析一个目录中所有的 string table 文件,返回一个 DataFrame 做为查询数据库"""
    print('Star translate {}'.format(game_path))
    total_entry_id_count = 0
    translated_id_count = 0

    duplicated_indexs = translate_df.index.get_duplicates()

    for dirpath, dirnames, filenames in os.walk(game_path):
        # data_expansion1/localized/en
        dirbase1_list = ('data_expansion1', 'data_expansion2', 'data')
        dirbase2 = 'localized'

        # 确认当前目录是否 OK
        # 1. 包含标准格式 data(data_exp1, data_exp2)/localized/ lan 
        # 2. 确认输出目录, 把 语言换成 sigua
        # 3. 把根换成 output 目录
        for dirbase1 in dirbase1_list:
            pos = os.path.normcase(dirpath.lower()).find('{}/{}/{}/text'.format(dirbase1, dirbase2, base_lan))
            if pos == -1:
                continue

            # 左边的截掉
            basedir = dirpath[pos:]
            # lan 换成 sigua
            basedir = basedir.replace('/{}/'.format(base_lan), '/sigua/')
            # 添加新的输出目录作为根
            output_fullpath = os.path.join(output_path, basedir)
            os.makedirs(output_fullpath, exist_ok=True)
            # print('Make dir {}'.format(output_fullpath))
            break
        # else:
        #     # 非文本存放目录
        #     continue

        for filename in filenames:
            # 跳过各种奇怪的文件
            if filename.startswith(("~", ".")):
                continue
            if not filename.endswith(".stringtable"):
                continue

            # # debug
            # # print(filename)
            # if filename == '00_bs_celby.stringtable':
            #     find = True
            #     pass

            full_filename = os.path.join(dirpath, filename)

            # 输出翻译之后的文件
            output_full_filename = os.path.join(output_fullpath, filename)

            # parse string table xml
            tree = ET.parse(full_filename)
            root = tree.getroot()

            name = root.find(TAG_STRING_TABLE_NAME).text



            for entry in root.iter(TAG_STRING_TABLE_ENTRY):
                translated = False                
                entry_id = entry.find(TAG_STRING_TABLE_ID)

                if entry_id is None:
                    print('empty entry_id {}'.format(name))
                    continue
                else:
                    entry_id_text = entry_id.text

                total_entry_id_count += 1

                default = entry.find(TAG_STRING_TABLE_DEFAULT_TEXT)
                female = entry.find(TAG_STRING_TABLE_FEMALE_TEXT)

                # 用Entry 字段内容和 ID 组成 Index, 做为 string 的索引
                key = get_key_string(dirbase1, name, entry_id_text)
                # key = u"[{}]_[{}]_[{}]_[{}]".format(dirbase1, filename.lower(), name, entry_id_text)
                # 找不到
                if key not in translate_df.index:
                    # print('Can not find {}'.format(key))
                    continue
                
                # 有多个结果
                translated_entry = translate_df.loc[key]
                if key in duplicated_indexs:
                    # print('Find multi result result with {}. Use 1st result'.format(key))
                    # print(translated_entry)
                    # print(translated_entry.index)
                    translated_entry = translated_entry.iloc[0]

                current_default_text = default.text
                current_female_text = female.text

                # always use first result 
                default_text = translated_entry[TAG_STRING_TABLE_DEFAULT_TEXT]
                female_text = translated_entry[TAG_STRING_TABLE_FEMALE_TEXT]

                if (not current_default_text) or (not has_Chinese(current_default_text)):
                    if default_text:
                        if need_add_space:
                            default.text = add_space(default_text)
                        else:
                            default.text = default_text
                        # print(default.text)
                        translated = True

                if (not current_female_text) or (not has_Chinese(current_female_text)):
                    if female_text:
                        if need_add_space:
                            female.text = add_space(female_text)
                        else:
                            female.text = female_text
                        # print(female.text)
                        translated = True
                
                if translated:
                    translated_id_count += 1
                    

                # if translate_df.loc[key, TAG_STRING_TABLE_DEFAULT_TEXT]:
                #     if need_add_space:
                #         default.text = add_space(translate_df.loc[key, TAG_STRING_TABLE_DEFAULT_TEXT])
                #     else:
                #         default.text = translate_df.loc[key, TAG_STRING_TABLE_DEFAULT_TEXT]
                #     # print(default.text)
                #     translated = True
                        
                # if translate_df.loc[key, TAG_STRING_TABLE_FEMALE_TEXT]:
                #     if need_add_space:
                #         female.text = add_space(translate_df.loc[key, TAG_STRING_TABLE_FEMALE_TEXT])
                #     else:
                #         female.text = translate_df.loc[key, TAG_STRING_TABLE_FEMALE_TEXT]
                #     # print(female.text)
                #     translated = True

            try:
                tree.write(output_full_filename, encoding="utf-8")
                if translated:
                    # print('{} translated to {}'.format(full_filename, output_full_filename))
                    pass
                else:
                    # print('{} use original version'.format(full_filename))
                    pass
                    

            except Exception as e:
                print(full_filename)
                print(e)
                print(tree)
    print('All files in {} translated to {}'.format(game_path, output_path))
    print('{} of {} has been translated'.format(translated_id_count, total_entry_id_count))



if __name__ == '__main__':
    # trow_path = './translate_group_result/trow'

    translate_result = (
        './translate_group_result/trow',
        './translate_group_result/Pillars.of.Eternity.ALI213.CHS.PATCH.V.4.4',
        './translate_group_result/3DMGAME-Pillars.of.Eternity.CHS.Patch.v6.0-3DM',
        "./translate_group_result/2015-07-07_Pillars of Eternity_CHT_v1.0_(For 1.06.0617)",
        "./translate_group_result/汉化版1.5正式版2",
        "./translate_group_result/tw",
        './translate_group_result/亚米蝶巨蟹_3.01',
        "./translate_group_result/3dm_5.0",
        "./translate_group_result/ali_4.0",
        "./translate_group_result/3DMv4.0+ALI213v1.5-Pillars.of.Eternity.CHT.v1.6",
        "./translate_group_result/cn_ali_3.5",
    )   


    for index, translate_path in enumerate(translate_result):
        df = parse_string_table_dir(translate_path)    

        if index == 0:
            translate(
                game_path='./string-table/en_3.05.1186/',
                output_path='./mod/',
                translate_df=df,
                base_lan='en',
                need_add_space=True
                )
        else:
            translate(
                game_path='./mod/',
                output_path='./mod/',
                translate_df=df,
                base_lan='sigua',
                need_add_space=True
                )            


    print('ALL Done')


# step 0
# 读取汉化组成果,生车汉化数据库

# step 1
# 读取原始游戏目录
# 原始游戏目录目前有三个子目录需要处理(1个主游戏+2个 DLC)
# /Users/brian/Documents/workplace/pillars_of_eternity_Chinese/translate_group_result/trow/Data/localized/ch/text/conversations/px1_00_stalwart_village/px1_00_cv_andred_byrhtwen.stringtable


# 解析每个字符表,尝试替换文本中的英文


# 生成新的汉化版本字符表


