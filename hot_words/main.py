import os
import random
import re
import string
from io import BytesIO
from typing import List, Union

import numpy as np
import pandas as pd
from fastapi import Body, FastAPI, File, Form, UploadFile, status
from fastapi.responses import FileResponse
from fuzzywuzzy import fuzz
from pypinyin import lazy_pinyin
from starlette.background import BackgroundTask
from xpinyin import Pinyin

#########################
#### fastapi构建后端api###
#########################
genius = FastAPI()


# 初始化一个拼音生成器实例
py_generator = Pinyin()


'''
-----------------读取系统已存在的热词-----------------
'''

def get_hot_words():
    hot_words = pd.read_csv('data/hot_words.csv')
    hot_words.fillna('', inplace=True)
    return hot_words

'''
---------------读取系统已存在的强制转换词-----------------
'''

def get_force_trans_ref():
    force_trans_ref = pd.read_csv('data/force_trans.csv')
    force_trans_ref = force_trans_ref.sort_values(
        by="keys", key=lambda x: x.str.len(), ascending=False).reset_index(drop=True)
    return force_trans_ref


'''
------------------特定词汇强制转化-------------------
'''


def force_trans(words: str):
    force_trans_ref = get_force_trans_ref()

    for key in force_trans_ref['keys']:
        values_list = force_trans_ref.loc[force_trans_ref.loc[:,
                                                              'keys'] == key, 'values'].values[0].split('、')
        for value in values_list:
            if value in words:
                words = words.replace(value, key)

    return words


'''
--------------方案：根据拼音全文模糊匹配---------------
'''


def replace_hot_word(module_name: str, words: str):
    try:
        # 强制转换特定词汇
        words = force_trans(words=words)
        # 获取系统热词
        hot_words = get_hot_words()
        # 生成拼音
        module_name_py = module_name + '_py'
        # hot_words[module_name_py] = hot_words[module_name].apply(
        #     lambda x: py_generator.get_pinyin(x))

        # 这里换用lazy_pinyin，因为lazy_pinyin对于对于多音字的词汇标注结果更准确，如会计-->kuai-ji而不是hui-ji
        hot_words[module_name_py] = hot_words[module_name].apply(
            lambda x: '-'.join(lazy_pinyin(x)))

        # 对热词按照长度降序排序，保证长热词优先替换
        hot_words = hot_words.sort_values(
            by=module_name, key=lambda x: x.str.len(), ascending=False)
        hot_words.reset_index(drop=True, inplace=True)
        
        # 禁忌列表，原文中被热词替换过的部分不会再参与替换，避免热词之间的相互替换
        forbidden_idx_list = []

        for j, hot_word_py in enumerate(hot_words[module_name_py].values):

            # py_generator的get_pinyin方法无法切割数字，导致后续替换时字符串的索引出错，所以需要自行构造切割
            words_changed = '-'.join(words)
            words_changed = py_generator.get_pinyin(words_changed).split('-')
            words_py = '-'.join(x for x in words_changed if x != '')

            # 为对齐热词文件的列长，部分公司出现了空值热词，需跳过
            if hot_word_py != '':

                # 字数>=4的热词阈值为70，否则为80
                if (len(hot_word_py.split('-')) >= 4):
                    threshold = 70
                else:
                    threshold = 80

                # 对于每一个热词，如果原文中存在该热词的拼音，则进行替换
                # 精确替换
                if hot_word_py in words_py:
                    # 一个字符串可能出现多次热词，需全部找出替换
                    iter_list = re.finditer(hot_word_py, words_py)
                    idx_list = [i.start() for i in iter_list]
                    for i in idx_list:
                        # 找出字符串中热词开始的索引
                        word_idx = len(words_py[:i].split('-')) - 1
                        # 找出热词的长度
                        word_py_idx = hot_words[hot_words[module_name_py]
                                                == hot_word_py].index[0]
                        length = len(hot_word_py.split('-'))
                        # 如果该索引部分的热词已经被替换过，则跳过
                        if (word_idx in forbidden_idx_list) or (word_idx+length-1 in forbidden_idx_list):
                            continue
                        # 替换
                        words = words[:word_idx] + \
                            hot_words.loc[word_py_idx, module_name] + \
                            words[word_idx+length:]
                        # 将已替换过热词的索引加入禁忌列表
                        forbidden_idx_list.extend(
                            range(word_idx, word_idx+length))

                # 模糊搜索，是既包含了精确搜索替换，但是实践发现模糊搜索会漏掉一部分精确搜索的结果，故依旧保留上面的精确搜索
                # 如果热词的拼音与字符串的拼音相似度大于等于阈值，即判定为匹配
                if fuzz.partial_ratio(words_py, hot_word_py) >= threshold:
                    # 但无法知道匹配开始的索引，故需要进一步搜索
                    # 设定搜索的长度为热词长度
                    group_size = len(hot_word_py.split('-'))
                    words_py_list = words_py.split('-')
                    iter_nums = len(words_py_list) - group_size + 1
                    k = 0
                    # 开始搜索
                    while k < iter_nums:
                        # 如果字符串中同长度词汇的拼音与热词的拼音相似度大于等于90，则判定匹配
                        if fuzz.ratio(hot_word_py, '-'.join(words_py_list[k:k+group_size])) >= 90:
                            # 确保热词未被替换过
                            if (k in forbidden_idx_list) or (k+group_size-1 in forbidden_idx_list):
                                k = k + 1
                                continue
                            # 替换热词
                            words = words[:k] + \
                                hot_words.loc[j, module_name] + \
                                words[k+group_size:]
                            # 将k到k+group_size的数字加入禁止forbidden_idx_list
                            forbidden_idx_list.extend(range(k, k+group_size))
                            # 查找下一个字符串中下一个热词
                            k = k + group_size
                        else:
                            # 搜索步长为1
                            k = k + 1

        return words, forbidden_idx_list
        # return words
    except:
        return TimeoutError


'''
--------------增添新热词方法---------------
'''


def append_new_words(companyName: str, companyHotWords: List[str]):
    try:
        # 获取已有热词
        hot_words = get_hot_words()
        # 如果该公司已经存在热词，则直接在原有热词后面追加新热词
        if companyName in hot_words.columns:
            new_words = pd.DataFrame(companyHotWords, columns=[companyName])
            hot_words = pd.concat(
                [hot_words, new_words], ignore_index=True)
        else:
            # 如果该公司不存在热词，则直接增加一列
            hot_words[companyName] = pd.Series(companyHotWords)
        # 去除每一列中的重复值
        hot_words[companyName] = hot_words[companyName].drop_duplicates()
        hot_words.dropna(how='all', inplace=True)
        # 去除每一列中的空值
        hot_words.fillna('', inplace=True)
        hot_words.to_csv('data/hot_words.csv', index=False)
        return {"status": "1"}
    except:
        return {"status": "0"}


'''
--------------在被替换的词前后插入tags，仅供查看---------------
'''


def insert_tags(text, idx_list):
    result = ""
    for text_idx in range(len(text)):
        if text_idx in idx_list:
            if (text_idx-1 not in idx_list) and (text_idx+1 not in idx_list):
                result += "<red>" + text[text_idx] + "</red>"
            elif (text_idx-1 not in idx_list) and (text_idx+1 in idx_list):
                result += "<red>" + text[text_idx]
            elif (text_idx-1 in idx_list) and (text_idx+1 not in idx_list):
                result += text[text_idx] + "</red>"
            else:
                result += text[text_idx]
        else:
            result += text[text_idx]
    return result


'''
-------------------查询热词------------------------
'''


@genius.get('/hot_words', status_code=status.HTTP_200_OK)
def query_hot_words(*, id: str = None):
    hot_words_query = get_hot_words()
    hot_words_query.fillna('', inplace=True)
    # 如果id不为空，则返回指定id的热词
    # 如果id为空，则返回所有热词
    if id:
        try:
            hot_words_query = pd.DataFrame(hot_words_query[id])
        except (KeyError):
            return {"status": "0", "message": "id not found"}

    # 将dataframe转换为dict,且去除每一列中的空值
    hot_words_dict = hot_words_query.to_dict(orient='Series')
    # 去除每一列中的空值
    for key in hot_words_dict.keys():
        hot_words_dict[key] = list(
            filter(lambda x: x != '', hot_words_dict[key]))
    return hot_words_dict


'''
-------------------以词update热词------------------------
'''


@genius.post('/update/with_words', status_code=status.HTTP_201_CREATED)
def update_hot_words_with_words(
    *,
    id: str = Body(...),
    companyHotWords: Union[str, List[str]] = Body(...)
):
    if isinstance(companyHotWords, str):
        # 将前端传入的热词字符串转换为list,，切割符号为','或者'，'
        companyHotWords = re.split(',|，', companyHotWords)
    elif isinstance(companyHotWords, list):
        pass
    response = append_new_words(id, companyHotWords)
    return response


'''
-------------------以文件update热词------------------------
'''


@genius.post('/update/with_file', status_code=status.HTTP_201_CREATED)
async def update_hot_words_with_file(
    *,
    id: str = Form(...),
    file: UploadFile = File(...)
):
    id = id
    try:
        companyHotWords = await file.read()
        companyHotWords = companyHotWords.decode('utf-8')
        companyHotWords = re.split(',|，', companyHotWords)
    except (AttributeError, UnicodeDecodeError):
        return {"status": "0", "message": "File Error! Please upload files that are separated by ',' or '，' in '.csv' or '.txt' format"}
    response = append_new_words(id, companyHotWords)
    return response


'''
-------------------对字符串进行热词替换------------------------
'''


@genius.post('/replace/with_words', status_code=status.HTTP_200_OK)
def replace_hot_words_with_words(
    *,
    id: str = Body(...),
    textContent: Union[str, List[str]] = Body(...),
):
    # 判断传入的text_content是否为list
    try:
        if isinstance(textContent, list):
            textContent = pd.Series(textContent).apply(
                lambda x: replace_hot_word(id, x))
            # # 将text_content转换为list
            # textContent = textContent.tolist()
        else:
            textContent = replace_hot_word(id, textContent)
    except (TimeoutError):
        return {"status": "0", "message": "Time out! Please try again later"}
    text_content = textContent.apply(lambda x: x[0])
    idx_list = textContent.apply(lambda x: x[1])
    idx_list.apply(lambda x: x.sort())
    replaced_text_content = []
    for i in range(len(text_content)):
        replaced_text_content.append(insert_tags(text_content[i], idx_list[i]))
    # return {"status": "1", "text_content": text_content.values.tolist(), "replaced_text_content": replaced_text_content}
    return {"status": "1", "text_content": text_content.values.tolist()}


'''
对文件中的字符串进行热词替换
模板即为系统导出的模板
'''


@genius.post('/replace/with_file', status_code=status.HTTP_200_OK)
async def replace_hot_words_with_file(
    *,
    id: str = Form(...),
    file: UploadFile = File(...),
):
    if file.filename.endswith('.csv'):
        textContent = pd.read_csv(file.file)
    elif file.filename.endswith('.xlsx'):
        textContent = pd.read_excel(BytesIO(file.file.read()))
    else:
        return {"status": "0", "message": "File Error! Please upload files that are separated by ',' or '，' in '.csv' or '.txt' format"}

    try:
        # 将对话内容中的热词替换为对应的热词,若对话内容为空，则不进行替换
        textContent['对话内容'] = textContent['对话内容'].apply(
            lambda x: replace_hot_word(id, x) if x is not np.nan else x)
        # 将替换后的对话内容写入到新的csv文件中，生成随机文件名
        random_filename = ''.join(random.sample(
            string.ascii_letters + string.digits, 8))
        random_filename = 'data/replaced_data/'+random_filename + '.csv'
        # 将替换后的对话内容暂时写入到csv文件中
        textContent.to_csv(random_filename, index=False)
        # 不管上传的文件是csv还是xlsx，都返回csv文件
        filename = re.sub('.csv|.xlsx', '', file.filename) + '_replaced.csv'

    except (TimeoutError):
        return {"status": "0", "message": "Time out! Please try again later"}
    
    # 返回替换后的对话内容的csv文件，并删除临时文件
    return FileResponse(random_filename, filename=filename, media_type='text/csv',
                        background=BackgroundTask(lambda: os.remove(random_filename)))

'''
---------------强制转换----------------
'''


@genius.post('/replace/force/with_words', status_code=status.HTTP_200_OK)
def replace_hot_words_with_words(
    *,
    id: str = Body(...),
    textContent: Union[str, List[str]] = Body(...),
):
    # 判断传入的text_content是否为list
    if id != '15414':
        return {"status": "0", "message": "ID not supported!"}
    try:
        if isinstance(textContent, list):
            textContent = pd.Series(textContent).apply(
                lambda x: force_trans(x))
            # 将text_content转换为list
            textContent = textContent.tolist()
        else:
            textContent = force_trans(textContent)
    except (TimeoutError):
        return {"status": "0", "message": "Time out! Please try again later"}

    return {"status": "1", "text_content": textContent}
