"""
Get DwarfFortress files from data dir,
extract names of behaviours mentioned
output to similarly named files in analysis directory
"""
import datetime
import re
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp
from bs4 import BeautifulSoup
import spacy

import analysis_case as AC
import utils

# Setup root_logger:
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
# Enums:

nlp = spacy.load("en_core_web_sm")

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    soup = None
    with open(filename,'rb') as f:
        text = f.read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(text, features='lxml')

    assert(soup is not None)
    data = extract_from_dev_log(soup)

    return data

def extract_from_dev_log(soup):
    dev_list = soup.find('ul')

    data = {}
    try:
        #Add (date : text)
        for li in dev_list.children:
            span = li.find('span')
            if span is None or span == -1:
                continue
            date = span.string
            text = li.get_text()
            text = text.replace(date,"")
            text = text.replace('\n',' ')
            data[date] = text
    except AttributeError:
        breakpoint()

    return data


def accumulator(new_data, accum_data, ctx):
    #accumulate all words to get frequencies
    for date,text in new_data.items():
        #TODO process dates

        #Accumulate text
        parsed = nlp(text)

        accum_data['__total_count'] += len(parsed)

        for sen in parsed.sents:
            # TODO create timeline of releases and features

            # Skip non-useful words
            for word in sen:
                if any([word.pos in [spacy.symbols.PUNCT, spacy.symbols.SPACE],
                        word.is_punct, word.is_space, word.is_stop]):
                    continue

                # accumulate lemmas
                word_lemma = word.lemma_.lower()
                if word_lemma not in accum_data:
                    accum_data['__unique_words'].add(word_lemma)
                    accum_data[word_lemma] = 0
                accum_data[word_lemma] += 1

            # count sentence lengths
            if len(sen) not in accum_data['__sen_counts']:
                accum_data['__sen_counts'][len(sen)] = 0
            accum_data['__sen_counts'][len(sen)] += 1

    return accum_data

def accumulator_final(data, ctx):
    #once accumulated, normalize?

    return data

if __name__ == "__main__":
    input_ext = ".html"
    output_lists = []
    output_ext = ".dev_log_analysis"

    init_accum = {
        '__total_count' : 0,
        '__sen_counts'  : {},
        '__unique_words' : set()
        }


    AC.AnalysisClass(__file__,
                     input_ext,
                     extract_from_file,
                     output_lists,
                     output_ext,
                     accumulator=accumulator,
                     accumulator_final=accumulator_final,
                     init_accum=init_accum)()
