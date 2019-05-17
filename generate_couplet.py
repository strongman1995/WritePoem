# -*- encoding:utf-8 -*-
import jieba
import os


class ChineseCouplet(object):
    def __init__(self, duilian_file, shi_file, all_shi_file):
        self.jieba_dict_file = "../data/词语-唐诗.txt"
        self.couplet = []
        self.couplet_poems = []
        self.all_poems = []
        self.up = ""
        self.up_seg = []
        self.down = ""
        self.down_seg = []
        self.candidates = {}
        self.ngram1 = {}
        self.ngram2 = {}
        self.ngram_condition_prob = {}
        self.ngram_sen = {}
        self.candidate_number = 5
        self.mini_prob = 0.0000000001
        jieba.load_userdict(self.jieba_dict_file)
        self.load_couplet(duilian_file)
        self.load_couplet_poems(shi_file)
        self.load_data(all_shi_file)

    def load_couplet(self, file_name):
        f = open(file_name)
        contents = []
        for line in f.xreadlines():
            contents.append(line.strip().decode("utf-8").split(" "))
        f.close()
        self.couplet = contents
        return

    def load_couplet_poems(self, file_name):
        f = open(file_name)
        contents = []
        for line in f.xreadlines():
            contents.append(line.strip().decode("utf-8").split(" "))
        f.close()
        self.couplet_poems = contents
        return

    def load_data(self, file_name):
        contents = []
        f = open(file_name)
        for line in f.xreadlines():
            lis = line.strip().split(" ")
            for l in lis:
                contents.append("0" + l.decode("utf-8") + "1")
        f.close()
        self.all_poems = contents
        return

    def set_up(self, up):  # 设置上联并断句,所有都是1-2字
        self.up = up
        self.up_seg = jieba.lcut(up)
        for phrase in self.up_seg:
            if len(phrase) > 2:
                index = self.up_seg.index(phrase)
                self.up_seg.remove(phrase)
                zi_n = len(phrase)
                i = zi_n - 1
                while (i >= 0):
                    self.up_seg.insert(index, phrase[i])
                    i = i - 1
        return

    def train(self):
        self.get_candidates2()
        self.get_ngram_count2()
        self.get_ngram_condition_prob()
        self.get_down()

        return

    def get_candidates2(self):
        for i, word in enumerate(self.up_seg):
            self.candidates[i] = {}
        for couplet in self.couplet:
            for i, half_couplet in enumerate(couplet):
                for j in range(len(self.up_seg)):
                    word = self.up_seg[j]
                    if word in half_couplet:
                        index = half_couplet.index(word)
                        word_n = len(word)
                        word_candidate = couplet[(i + 1) % 2][index:(index + word_n)]
                        if word_candidate in self.candidates[j].keys():
                            self.candidates[j][word_candidate] += 1
                        else:
                            self.candidates[j][word_candidate] = 1
        # up_seg_2 = [word for j, word in enumerate(self.up_seg) if len(self.candidates[j]) < self.candidate_number]
        for couplet in self.couplet_poems:
            for i, half_couplet in enumerate(couplet):
                for j in range(len(self.up_seg)):
                    word = self.up_seg[j]
                    if word in half_couplet:
                        index = half_couplet.index(word)
                        word_n = len(word)
                        word_candidate = couplet[(i + 1) % 2][index:(index + word_n)]
                        if word_candidate in self.candidates[j]:
                            self.candidates[j][word_candidate] += 0.0001
                        else:
                            self.candidates[j][word_candidate] = 0.0001
        for j, word in enumerate(self.up_seg):
            dict_to_sort = self.candidates[j]
            if (len(dict_to_sort.items()) < self.candidate_number):
                n = len(dict_to_sort.items())
            else:
                n = self.candidate_number
            dict_sorted = dict(sorted(dict_to_sort.items(), key=lambda x: x[1], reverse=True)[:n])
            self.candidates[j] = dict_sorted
        self.candidates[-1] = {"0": 1}
        self.candidates[len(self.up_seg)] = {"1": 1}
        return

    def see_candidate(self):
        for i in self.candidates.keys():
            if (i != -1) and (i != len(self.up_seg)):
                print self.up_seg[i] + ": " + "   ".join(self.candidates[i].keys())
        return

    def get_ngram_count2(self):
        ngram1 = []
        for i in self.candidates.keys():
            for word in self.candidates[i]:
                ngram1.append(word)
        ngram1 = list(set(ngram1))
        for word in ngram1:
            self.ngram1[word] = 0
        ngram2 = []
        for i in self.candidates.keys():
            if i < len(self.up_seg):
                # print i
                for word1 in self.candidates[i].keys():
                    for word2 in self.candidates[i + 1].keys():
                        # print word1+word2
                        ngram2.append(word1 + " " + word2)
        ngram2 = list(set(ngram2))
        for word in ngram2:
            self.ngram2[word] = 0
        ngram1.remove("0")
        ngram1.remove("1")
        for sentence in self.all_poems:
            for word in ngram1:
                if word in sentence:
                    self.ngram1[word] += 1
            for word in ngram2:
                word_raw = word.replace(" ", "")
                if word_raw in sentence:
                    self.ngram2[word] += 1
        self.ngram1["0"] = len(self.all_poems)
        return

    def get_ngram_condition_prob(self):
        for i in self.candidates.keys():
            if (i < len(self.up_seg)):
                for word1 in self.candidates[i].keys():
                    if word1 not in self.ngram_condition_prob.keys():
                        self.ngram_condition_prob[word1] = {}
                    for word2 in self.candidates[i + 1].keys():
                        fenzi = self.ngram2[word1 + " " + word2]
                        if (fenzi == 0):
                            fenzi = self.mini_prob
                        fenmu = self.ngram1[word1]
                        self.ngram_condition_prob[word1][word2] = 1.0 * fenzi / fenmu
        return

    def get_down(self):
        self.ngram_sen[0] = {}
        for word in self.candidates[0]:
            sen = "0 " + word
            self.ngram_sen[0][sen] = self.ngram_condition_prob["0"][word]
        for i in range(len(self.up_seg)):
            level = i + 1
            self.ngram_sen[level] = {}
            for word in self.candidates[level].keys():
                max_sen = ""
                max_prob = -1
                for sen_before in self.ngram_sen[level - 1].keys():
                    prob_before = self.ngram_sen[level - 1][sen_before]
                    last_word = sen_before.split(" ")[-1]
                    now_prob = prob_before * self.ngram_condition_prob[last_word][word]
                    if (now_prob > max_prob):
                        max_prob = now_prob
                        max_sen = sen_before + " " + word
                self.ngram_sen[level][max_sen] = max_prob
                print max_sen
        last_sen = max_sen.replace(" ", "")[1:-1]
        self.down = last_sen
        return
