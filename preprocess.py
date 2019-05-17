# -*- coding: utf-8 -*-

import os
import re
import time
import codecs
import argparse

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
BASE_FOLDER = os.path.abspath(os.path.dirname(__file__)).decode('gb2312')
DATA_FOLDER = os.path.join(BASE_FOLDER, 'data')
DEFAULT_FIN = os.path.join(DATA_FOLDER, u'唐诗语料库.txt')
DEFAULT_FOUT = os.path.join(DATA_FOLDER, 'poem.txt')
reg_noisy = re.compile(u'[^\u3000-\uffee]')
reg_note = re.compile(u'(（.*）)') # Cannot deal with （） in seperate lines
# 中文及全角标点符号(字符)是\u3000-\u301e\ufe10-\ufe19\ufe30-\ufe44\ufe50-\ufe6b\uff01-\uffee

def set_arguments():
    parser = argparse.ArgumentParser(description='Pre process')
    parser.add_argument('--fin', type=unicode, default=DEFAULT_FIN,
                        help=u'Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fout', type=unicode, default=DEFAULT_FOUT,
                        help=u'Output file path, default is {}'.format(DEFAULT_FOUT))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    fd = codecs.open(cmd_args.fin, 'r', 'utf-8')
    fw = codecs.open('data/poem_temp.txt', 'w', 'utf-8')
    reg = re.compile(u'〖(.*)〗')
    start_flag = False
    for line in fd:
        line = line.strip()
        if not line or u'《全唐诗》' in line or '<http'  in line or u'□' in line:
            continue
        elif u'〖' in line and u'〗' in line:
            if start_flag:
                fw.write('\n')
            start_flag = True
            g = reg.search(line)
            if g:
                fw.write(g.group(1))
                fw.write('\n')
            else:
                # noisy data
                print(line)
        else:
            line = reg_noisy.sub('', line)
            line = reg_note.sub('', line)
            line = line.replace(' .', '')
            fw.write(line)

    fd.close()
    fw.close()

    fd = codecs.open('data/poem_temp.txt', 'r', 'utf-8')
    fw = codecs.open(cmd_args.fout, 'w', 'utf-8')
    title_flag = False
    for line in fd:
        line = line.strip()
        title_flag = not title_flag
        if title_flag:
            title = line + '\n'
            continue
        else:
            subline = re.split(ur'。|，', line)
            if len(subline) - 1 % 2 == 1:
                continue
            flag = True
            length = len(subline[0])
            for s in subline[:-1]:
                if len(s) != 5 and len(s) != 7 or len(s) != length:
                    flag = False
                    break
            if flag == True:
                fw.write(title)
                fw.write(line + '\n')
    fd.close()
    fw.close()
    print('{} STOP'.format(time.strftime(TIME_FORMAT)))