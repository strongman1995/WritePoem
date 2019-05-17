# -*- coding: utf-8 -*-

import os
import time
import flask
from flask import render_template, request, g
import random
import argparse

import generate_poem
from generate_couplet import ChineseCouplet

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
BASE_FOLDER = os.path.abspath(os.path.dirname(__file__)).decode('gb2312')
DATA_FOLDER = os.path.join(BASE_FOLDER, 'data')
DEFAULT_FCOLLOCATIONS_V = os.path.join(DATA_FOLDER, 'collocations_v')
DEFAULT_FCOLLOCATIONS_H = os.path.join(DATA_FOLDER, 'collocations_h')
DEFAULT_FWORDS = os.path.join(DATA_FOLDER, 'words')
DEFAULT_FTOPIC_WORDS = os.path.join(DATA_FOLDER, 'topic_words')
DEFAULT_FSTART_WORDS = os.path.join(DATA_FOLDER, 'start_words.txt')

collocations_v = generate_poem.read_dump(DEFAULT_FCOLLOCATIONS_V)
collocations_h = generate_poem.read_dump(DEFAULT_FCOLLOCATIONS_H)
words = generate_poem.read_dump(DEFAULT_FWORDS)
topic_words = generate_poem.read_dump(DEFAULT_FTOPIC_WORDS)
start_words = generate_poem.read_txt(DEFAULT_FSTART_WORDS)

app = flask.Flask(__name__)

def set_arguments():
    parser = argparse.ArgumentParser(description='Poem Generator')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='host, default is 127.0.0.1.')
    parser.add_argument('--port', type=int, default='5001',
                        help='port, default is 5001.')
    return parser


@app.route('/', methods = ['GET', 'POST'])
def index():
    if request.method == 'POST':
        sentences_count = 4
        poem = ['' for i in range(sentences_count)]
        poem_1 = request.form['poem_1']
        poem_2 = request.form['poem_2']
        poem_3 = request.form['poem_3']
        poem_4 = request.form['poem_4']
        if poem_1: # 用户给了诗句
            ###
            # poem.append(poem_1)
            # duilian_file = "data/对联-唐诗-5言或7言.txt"
            # shi_file = "data/对联-唐诗.txt"
            # all_shi_file = "data/唐诗句子.txt"
            # coup = ChineseCouplet(duilian_file, shi_file, all_shi_file)
            #
            # coup.set_up(poem_1)
            # coup.train()
            # poem.append(coup.down)
            # print coup.down
            # topic_id = random.randint(0, 9)
            # sentence_len = len(poem_1)
            # start_word = random.choice(start_words)
            # up2 = generate_poem.generate_first_sentence(start_word, sentence_len, topic_words[topic_id], words,collocations_h)
            # up2 = ''.join(up2)
            # print up2
            # poem.append(up2)
            # coup.set_up(up2)
            # coup.train()
            # poem.append(coup.down)
            # print coup.down
            ###
            topic_id = random.randint(0, 9) #TODO
            given_poem = [poem_1, poem_2, poem_3, poem_4]
            sentence_len = len(given_poem[0])
            flag = False
            for tried_count in range(3):
                poem = generate_poem.generate_poem_with_poem4(given_poem,collocations_v, collocations_h, words, topic_words[topic_id])
                print '\n'.join(poem)
                flag = True
                for i in range(4):
                    if len(poem[i]) != sentence_len:
                        flag = False
                        break
                if flag:
                    break
            if not flag:
                poem = [u'系统暂无法生成', u'请您稍候再尝试', u'很抱歉带来困扰', u'感谢您的使用啦']
        else:
            topic_id = random.randint(0, 9)
            sentence_len = 7
            start_word = random.choice(start_words)
            flag = False
            for tried_count in range(3):
                poem = generate_poem.generate_poem(sentence_len, sentences_count, start_word,\
                    collocations_v, collocations_h, words, topic_words[topic_id])
                print(poem)
                flag = True
                for i in range(4):
                    if len(poem[i]) != sentence_len:
                        flag = False
                        break
                if flag:
                    break
            if not flag:
                poem = [u'系统暂无法生成', u'请您稍候再尝试', u'很抱歉带来困扰', u'感谢您的使用啦']

        return render_template('index.htm',
                                poem_1=poem[0],
                                poem_2=poem[1],
                                poem_3=poem[2],
                                poem_4=poem[3])
    return render_template('index.htm', g = g)


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START {}:{}'.format(time.strftime(TIME_FORMAT), cmd_args.host, cmd_args.port))

    app.run(host='0.0.0.0', port=cmd_args.port)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))