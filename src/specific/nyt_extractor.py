"""
Get headlines from nyt jsons from data dir,

output to similarly named files in analysis directory
"""
import numpy as np
import datetime
import spacy
from textblob import TextBlob
import json
from random import choice
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp
from os.path import splitext, split
import logging as root_logger

import analysis_case as AC
import utils

# Setup root_logger:
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################

nlp = spacy.load("en_core_web_sm")

only_allow = ["article"]
date_fmt = "%Y-%m-%dT%H:%M:%SZ"

class NYT_Entry(utils.ParseBase):

    def __init__(self, doc_type,
                 date, url,
                 lead_paragraph, print_page, id_,
                 headline=None, desk=None):
        super().__init__()
        self._type = doc_type
        self._headline = headline
        self._date = date
        self._url = url
        self._paragraph = lead_paragraph
        self._page = print_page
        self._id = id_

    def __str__(self):
        s = "{} : {} : {} : {}".format(self._line_no,
                                        self._date,
                                        self._type,
                                        self._page)

        return s

    def parse_date(self):
        date_str = self._date
        the_date = datetime.datetime.strptime(date_str, date_fmt)
        return the_date


def make_entry(current):
    lookup_keys = ['document_type', 'pub_date', 'web_url', 'lead_paragraph', 'print_page', '_id']
    lookup_values = [current[x] if x in current else "missing"  for x in lookup_keys]

    desk_keys = ['news_desk','section_name','subsection_name']
    q = [current[x] if x in current else "_" for x in desk_keys]
    w = [x for x in q if x is not None]
    desk_value = ".".join(w)

    if 'headline' in current and 'main' in current['headline']:
        headline = current['headline']['main']
    elif 'headline' in current and 'print_headline' in current['headline']:
        headline = current['headline']['print_headline']
    else:
        headline = "missing"

    entry = NYT_Entry(*lookup_values,
                      headline=headline,
                      desk=desk_value.replace(' ','_'))

    return entry

def extract_from_file(filename):
    logging.info("Extracting from: {}".format(filename))
    data = { 'key_set' : set(),
             'document_type_set' : set(),
             'entity_set' : set(),
             'entries' : [],
             'id_sequence' : []
             }
    headline_vectors = None
    ngram_counts = {}
    posgram_counts = {}
    raw_json = []
    with open(filename,'r') as f:
        raw_json = json.load(f)

    docs = raw_json['response']['docs']

    state = { 'bracket_count' : 0,
              'current' : None,
              'entry' : 0,
              'counter' : 0,
              'counter_reset' : int(len(docs) / 100)
              }

    while bool(docs):
        state['entry'] += 1
        state['counter'] += 1
        if state['counter'] > state['counter_reset']:
            logging.info("...")
            state['counter'] = 0

        current = docs.pop(0)

        data['key_set'].update(current.keys())
        data['document_type_set'].add(current['document_type'])

        entry = make_entry(current)
        entry._line_no = state['entry']

        parsed_headline = nlp(entry._headline)
        # parsed_paragraph = nlp(entry._paragraph)

        data['entity_set'].update([x for x in parsed_headline.ents])

        if entry._type in only_allow:
            data['entries'].append(entry)

        blob = TextBlob(entry._headline.lower())
        pos_blob = TextBlob(" ".join([x.tag_ for x in parsed_headline]))
        # TODO Counts
        # TODO verb pairs
        # TODO heading lengths
        # TODO POS ngrams
        ngrams = blob.ngrams(n=2)
        posgrams = pos_blob.ngrams(n=3)

        for triple in ngrams:
            joined = " ".join(triple)
            if joined not in ngram_counts:
                ngram_counts[joined] = 0
            ngram_counts[joined] += 1

        for triple in posgrams:
            joined = " ".join(triple)
            if joined not in posgram_counts:
                posgram_counts[joined] = 0
            posgram_counts[joined] += 1

        # use parsed_headline.vector to cluster
        data['id_sequence'].append(entry._id)
        if headline_vectors is None:
            headline_vectors = parsed_headline.vector
        else:
            headline_vectors = np.row_stack((headline_vectors,
                                             parsed_headline.vector))

    data['key_set'] = list(data['key_set'])
    data['document_type_set'] = list(data['document_type_set'])

    # Save other files:
    basename = splitext(split(filename)[1])[0]
    with open(join('analysis',
                   "{}.vectors".format(basename)),
              'wb') as f:
        headline_vectors.dump(f)

    with open(join('analysis',
                   "{}_ngrams.json".format(basename)),
              'w') as f:
        json.dump(ngram_counts, f)

    with open(join('analysis',
                   "{}_posgrams.json".format(basename)),
              'w') as f:
        json.dump(posgram_counts, f)

    return data



if __name__ == "__main__":

    queue = join("/Volumes", "DOCUMENTS", "nyt_data")
    output_lists = ['entries']
    output_ext = ".nyt_analysis"

    AC.AnalysisCase(queue,
                    ".json",
                    extract_from_file,
                    output_lists,
                    output_ext)()
