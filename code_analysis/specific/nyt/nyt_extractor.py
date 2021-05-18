"""
Get headlines from nyt jsons from data dir,

output to similarly named files in analysis directory
"""
import datetime
import json
import logging as root_logger
from enum import Enum
from os import listdir
from os.path import (abspath, exists, expanduser, isdir, isfile, join, split,
                     splitext)
from random import choice, shuffle

import code_analysis.util.analysis_case as AC
import numpy as np
import pyparsing as pp
import spacy
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState
from textblob import TextBlob

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

def extract_from_file(filename, ctx):
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
    target = join("/Volumes", "DOCUMENTS", "nyt_data")

    AC.AnalysisCase(__file__,
                    ".json",
                    extract_from_file,
                    targets=[target])()
