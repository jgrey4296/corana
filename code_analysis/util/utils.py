##-- imports
import argparse
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from time import sleep
from fractions import Fraction
from random import choice, shuffle
import json
from enum import Enum
import logging as root_logger
import requests
##-- end imports

logging = root_logger.getLogger(__name__)

CONCEPT_NET_API = "http://api.conceptnet.io{}"


def search_conceptnet(concept):
    """ Rate Limit: 3600 an hour, 120 a minute.
    Average at 1 per second
    Expect concept to start with a /
    """
    assert(concept[0] == "/")
    sleep(1)
    return requests.get(CONCEPT_NET_API.format(concept)).json()


def map_text(text):
    """ Given some text, create a mapping to integers and back """
    #todo: enable it to work for tokens as well
    chars = sorted(list(set(text)))
    char_indices = dict((c, i) for i, c in enumerate(chars))
    indices_char = dict((i, c) for i, c in enumerate(chars))
    return (char_indices, indices_char)

def sample(predictions, temperature=1.0):
    """ For a word mapping M:{i : char} dictionary, give [] of len(M) of predictions of
    the next index. Normalize it and sample, taking the highest. Return that index """
    #cast to high precision?
    preds = np.asarray(predictions).astype('float64')
    preds = np.log(pres) / temperature
    exp_preds = np.exp(preds)
    #normalize
    preds = exp_preds / np.sum(exp_preds)
    probabilities = np.random.multinomial(1, preds, 1)
    return np.argmax(probas)


def guarded_log(msg, val):
    if isinstance(val, str) and bool(val.strip()):
        logging.info(msg.format(val))

def get_data_files(initial, ext=None, normalize=False):
    """
    Getting all files of an extension
    """
    logging.info("Getting Data Files")
    if ext is None:
        ext = []

    if not isinstance(ext, list):
        ext = [ext]
    if not isinstance(initial, list):
        initial = [initial]

    unrecognised_types = set()
    files = []
    queue = [abspath(expanduser(x)) for x in initial]
    while bool(queue):
        current = queue.pop(0)
        ftype = splitext(current)[1].lower()
        match_type = not bool(ext) or ftype in ext
        missing_type = ftype not in unrecognised_types

        if isfile(current) and match_type:
            files.append(current)
        elif isfile(current) and not match_type and missing_type:
            logging.warning("Unrecognized file type: {}".format(splitext(current)[1].lower()))
            unrecognised_types.add(ftype)
        elif isdir(current):
            sub = [join(current,x) for x in listdir(current)]
            queue += sub


    logging.info("Found {} {} files".format(len(files), ext))
    if normalize:
        files = [norm_unicode("NFD", x) for x in files]
    return files
