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
DEFAULT_FCOLLOCATIONS_V = os.path.join(DATA_FOLDER, 'collocations_v')
DEFAULT_FCOLLOCATIONS_H = os.path.join(DATA_FOLDER, 'collocations_h')
reg_sep = re.compile(u'([^\u4e00-\u9fa5]+)')


class BigramCollocationFinder():
    def __init__(self):
        self.bigram_fd = dict()
        self.N = 0

    def add_word_pair(self, word_pair):
        self.N += 1
        self.bigram_fd[word_pair] = self.bigram_fd.get(word_pair, 0) + 1

    def score_bigram(self, measure):
        """
        计算词频
        :param measure:
        :return:
        """
        score = []
        if measure == 'frequency':
            for word_pair in self.bigram_fd:
                score.append((word_pair, float(self.bigram_fd[word_pair]) / self.N))
        else:
            print('Unknown measure!')
        return score


# def read_data(fin):
#     """
#     读取数据，并且进行分句，切词，生成词对的预处理
#     """
#     finder_v = BigramCollocationFinder()
#     finder_h = BigramCollocationFinder()
#     title_flag = False
#     fd = codecs.open(fin, 'r', 'utf-8')
#     for line in fd:
#         line = line.strip()
#         title_flag = not title_flag
#         if title_flag:
#             continue
#         sentences = reg_sep.sub(' ', line).split()
#         if len(sentences) % 2 > 0: # 不分析奇数句的诗歌
#             continue
# #         sentences = [list(jieba.cut(i)) for i in sentences]
# #         print ' '.join(sentences[0])
#         cut_sentences = []
#         for i in range(0, len(sentences), 2):
#             up = jieba.lcut(sentences[i])
#             if len(up) == 1:# jieba 没切,手动切
#                 if len(sentences[i]) == 5:
#                     up = [sentences[i][:2],sentences[i][2:]]
#                 elif len(sentences[i]) == 7:
#                     up = [sentences[i][:2],sentences[i][2:4],sentences[i][4:]]
#             down = list()
#             s,e = 0,0
#             for k in range(len(up)):
#                 l = len(up[k])
#                 e = s + l
#                 down.append(sentences[i+1][s:e])
#                 s = e
#             cut_sentences.append(up)
#             cut_sentences.append(down)
#         for i in range(0, len(cut_sentences), 2):
#             for j in range(len(cut_sentences[i])):
#                 if len(cut_sentences[i][j]) == len(cut_sentences[i + 1][j]): # 切词后 上下句对应位置的词长相同，加入到词对finder_v的word_pair中
#                     finder_v.add_word_pair((cut_sentences[i][j], cut_sentences[i + 1][j]))
#                 else:
#                     break
#                 if j + 1 < len(cut_sentences[i]):# 切词后，同一句中的相邻的词加入finder_h的word_pair中
#                     finder_h.add_word_pair((cut_sentences[i][j], cut_sentences[i][j + 1]))
#                     finder_h.add_word_pair((cut_sentences[i + 1][j], cut_sentences[i + 1][j + 1]))
#     fd.close()
#     print('Read data done.')
#     return (finder_v, finder_h)

def read_data(fin):
    finder_v = BigramCollocationFinder()
    finder_h = BigramCollocationFinder()
    title_flag = False
    fd = codecs.open(fin, 'r', 'utf-8')
    for line in fd:
        line = line.strip()
        title_flag = not title_flag
        if title_flag:
            continue
        sentences = reg_sep.sub(' ', line).split()
        if len(sentences) % 2 > 0:
            continue
        sentences = [list(jieba.cut(i)) for i in sentences]
        for i in range(0, len(sentences), 2):
            if len(sentences[i]) != len(sentences[i + 1]):
                continue
            for j in range(len(sentences[i])):
                if len(sentences[i][j]) == len(sentences[i + 1][j]):
                    finder_v.add_word_pair((sentences[i][j], sentences[i + 1][j]))
                else:
                    break
                if j + 1 < len(sentences[i]):
                    finder_h.add_word_pair((sentences[i][j], sentences[i][j + 1]))
                    finder_h.add_word_pair((sentences[i + 1][j], sentences[i + 1][j + 1]))
    fd.close()
    print('Read data done.')
    return (finder_v, finder_h)

def get_collocations_from_finder(finder):
    """
    生成collocation dict
    {w1:{l1:[(score_1,w2_1),(score_2,w2_2)],
         l2:[(score_1,w2_1),(score_2,w2_2)],...},
     w2:{l1:[(score_1,w2_1),(score_2,w2_2)],
         l2:[(score_1,w2_1),(score_2,w2_2)],...},
     ...
     }
    :param finder:
    :return:
    """
    measure = 'frequency'
    collocations = finder.score_bigram(measure)
    collocations = sorted(collocations, key=lambda x: x[1], reverse=True)
    collocations_dict = dict()
    for (w1, w2), score in collocations:
        l = len(w2)
        if w1 in collocations_dict:
            if l in collocations_dict[w1]:
                collocations_dict[w1][l].append((score, w2))
            else:
                collocations_dict[w1][l] = [(score, w2)]
        else:
            collocations_dict[w1] = {l: [(score, w2)]}
    return collocations_dict


def write_collocations(fout, collocations):
    """
    将collocations持久化到fout
    :param fout:
    :param collocations:
    :return:
    """
    fw = codecs.open(fout, 'wb')
    pickle.dump(collocations, fw)
    fw.close()
    print('Write collocations done.')


def set_arguments():
    parser = argparse.ArgumentParser(description='Get collocations')
    parser.add_argument('--fin', type=unicode, default=DEFAULT_FIN,
                        help=u'Input file path, default is {}'.format(DEFAULT_FIN))
    parser.add_argument('--fcollocations_v', type=unicode, default=DEFAULT_FCOLLOCATIONS_V,
                        help=u'Output collocations_v file path, default is {}'.format(DEFAULT_FCOLLOCATIONS_V))
    parser.add_argument('--fcollocations_h', type=unicode, default=DEFAULT_FCOLLOCATIONS_H,
                        help=u'Output collocations_h file path, default is {}'.format(DEFAULT_FCOLLOCATIONS_H))
    return parser


if __name__ == '__main__':
    parser = set_arguments()
    cmd_args = parser.parse_args()

    print('{} START'.format(time.strftime(TIME_FORMAT)))

    (finder_v, finder_h) = read_data(cmd_args.fin)
    collocations_v = get_collocations_from_finder(finder_v)
    collocations_h = get_collocations_from_finder(finder_h)
    write_collocations(cmd_args.fcollocations_v, collocations_v)
    write_collocations(cmd_args.fcollocations_h, collocations_h)

    print('{} STOP'.format(time.strftime(TIME_FORMAT)))
