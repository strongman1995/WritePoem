# -*- coding: utf-8 -*-

import os
import re
import time
import jieba
import codecs
import pickle
import argparse

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
BASE_FOLDER = os.path.abspath(os.path.dirname(__file__)).decode('gb2312')
DATA_FOLDER = os.path.join(BASE_FOLDER, 'data')
DEFAULT_FIN = os.path.join(DATA_FOLDER, 'poem.txt')
DEFAULT_FOUT = os.path.join(DATA_FOLDER, 'start_words.txt')


def read_data(fin):
    """
    读取poem.txt
    对诗句切词，统计每句诗歌中的第一个词
    :param fin:
    :return:
    """
    start_words = dict()
    title_flag = False
    fd = codecs.open(fin, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        title_flag = not title_flag
        if title_flag or not line:
            continue
        word = list(jieba.cut(line))[0]
        start_words[word] = start_words.get(word, 0) + 1
    fd.close()
    print('Read data done.')
    return start_words


def write_start_words(fout, start_words):
    """
    将 词长大于1 词频大于10 的起始词 保存到fout中
    :param fout:
    :param start_words:
    :return:
    """
    fw = codecs.open(fout, 'w', 'utf-8')
    for k, v in start_words.items():
        if v > 10 and len(k) > 1:
            fw.write(k + '\n')
    fw.close()
    print('Write start_words done.')


def set_arguments():
    parser = argparse.ArgumentParser(description='Get topics')
    parser.add_argument('--fin', type=unicode, default=DEFAULT_FIN,
                        help=u'Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fout', type=unicode, default=DEFAULT_FOUT,
                        help=u'Output start_words file path, default is {}'.format(DEFAULT_FOUT))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    start_words = read_data(cmd_args.fin)
    write_start_words(cmd_args.fout, start_words)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))
