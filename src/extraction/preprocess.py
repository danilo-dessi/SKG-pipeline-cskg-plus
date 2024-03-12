import os
import json
import nltk
from tqdm import tqdm
import shutil


def inverted_index_to_str(inverted_index_dict):
    string_len = 0
    for k, indexes in inverted_index_dict.items():
        for el in indexes:
            if el > string_len:
                string_len = el

    token_list = [' ']*(string_len+1)

    for k, indexes in inverted_index_dict.items():
        for el in indexes:
            token_list[el] = k

    return ' '.join(token_list)


def tokenize(text):
    sentences_tokenized = []
    try:
        sentences = nltk.sent_tokenize(text)
        for s in sentences:
            tokens = [t for t in nltk.word_tokenize(s.encode('utf8', 'ignore').decode('ascii', 'ignore')) if t not in ['']]
            # sentences: maximum 250 tokens, at least 5 tokens, at maximum 5 dots
            if len(tokens) <= 250 and len(tokens) >= 5:
                sentences_tokenized += [tokens]
    except:
        pass
    return sentences_tokenized


def saveDyGIEpp(paper2info, filename, dygiepp_dir):

    number_of_elements_per_file = 15000
    counter = 0

    fw = open(dygiepp_dir + str(int(counter / number_of_elements_per_file)) + '_' + filename, 'w+')
    for paper, info in paper2info.items():
        json.dump({
            'clusters': [[] for x in range(len(info['sentences']))],
            'sentences': info['sentences'],
            'ner': [[] for x in range(len(info['sentences']))],
            'relations': [[] for x in range(len(info['sentences']))],
            'doc_key': paper,
            'dataset': 'scierc'
        }, fw)
        fw.write('\n')

        counter += 1
        if counter % number_of_elements_per_file == 0:
            fw.flush()
            fw.close()
            fw = open(dygiepp_dir + str(int(counter / number_of_elements_per_file)) + '_' + filename, 'w+')

    fw.flush()
    fw.close()


def saveOther(paper2info, filename, other_dir):

    number_of_elements_per_file = 15000
    counter = 0

    fw = open(other_dir + str(int(counter % number_of_elements_per_file)) + '_' + filename, 'w+')
    for paper, info in paper2info.items():
        json.dump({
            'doc_key': paper,
            'year': info['year'],
            'doi': info['doi']
        }, fw)
        fw.write('\n')

        counter += 1
        if counter % number_of_elements_per_file == 0:
            fw.flush()
            fw.close()
            fw = open(other_dir + str(int(counter / number_of_elements_per_file)) + '_' + filename, 'w+')

    fw.flush()
    fw.close()



if __name__ == '__main__':

    input_dir = '../../data/original/'
    dygiepp_dir = '../../data/processed/dygiepp_input/'
    other_dir = '../../data/processed/other_info/'
    done_dir = '../../data/done/'

    if not os.path.exists(dygiepp_dir):
        os.mkdir(dygiepp_dir)

    if not os.path.exists(other_dir):
        os.mkdir(other_dir)

    files = os.listdir(input_dir)


    #files = set([x for x in files for y in os.listdir(other_dir) if x not in y and '.jsonl' in x])
    #print(files)
    #exit(1)

    for file in files:
        print('>> processing:', input_dir+file)
        paper2info = {}
        with open(input_dir+file, 'r') as f:
            pbar = tqdm(list(f))
            try:
                for line in pbar:
                    line_content = json.loads(line)

                    abstract = inverted_index_to_str(line_content['a'])
                    abstract_tokenized = tokenize(abstract)

                    title_tokenized = tokenize(line_content['t'])
                    sentences = title_tokenized + abstract_tokenized

                    if len(sentences) > 1:
                        paper2info[line_content['i']] = {}
                        paper2info[line_content['i']] = {
                            'doc_key' : line_content['i'],
                            'sentences' : sentences,
                            'title' : line_content['t'],
                            'abstract' : abstract,
                            'year' : line_content['p'],
                            'doi': line_content['d']
                        }

                print('>> saving', input_dir + file)
                saveDyGIEpp(paper2info, file, dygiepp_dir)
                saveOther(paper2info, file, other_dir)

                print('>> done:', input_dir + file, 'paper number:', len(paper2info), '\n')
                shutil.move(input_dir + file, done_dir + file)
            except:
                print('ERROR on ', file)







