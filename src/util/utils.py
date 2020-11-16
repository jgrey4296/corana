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
logging = root_logger.getLogger(__name__)



class ParseBase:

    def __init__(self):
        self._type = None
        self._name = None
        self._components = []
        self._args = []
        self._line_no = -1

    def __repr__(self):
        return "({} : {} : {})".format(self._line_no,
                                       self._type,
                                       self._name)

    def __str__(self):
        data = {}

        if bool(self._args):
            data.update({ 'args': [str(x) for x in self._args]})

        if bool(self._components):
            if not hasattr(self._components[0], 'to_dict'):
                data.update({ 'components' : [str(x) for x in self._components]})
            else:
                data.update({ 'components' : [x.to_dict() for x in self._components]})

        s = "{} : {} : {} := {}"

        return s.format(self._line_no,
                        self._type,
                        self._name,
                        json.dumps(data))

    def __lt__(self, other):
        return self._line_no < other._line_no



class Trie:

    def __init__(self, value, path, example=None):
        self.count = 0
        self.value = value
        self.path = "{} {}".format(path, value)
        self.data = {}
        self._example = example

    def __repr__(self):
        #Print all paths to leaves
        return "\n".join(self.leaves())

    def __bool__(self):
        """ Is Node populated? """
        return bool(self.data)

    def get(self, key):
        if key not in self.data:
            self.data[key] = Trie(key, self.path)

        return self.data[key]

    def inc(self):
        self.count += 1

    def add_string(self, theList, transform=None, example=None):
        if transform is None:
            transform = lambda x: x
        current = self
        for val in theList:
            val_prime = transform(val)
            current = current.get(val_prime)
            current.inc()
        if example and current._example is None:
            current._example = example

    def leaves(self):
        leaves = []
        queue = [self]
        while queue:
            node = queue.pop(0)
            if not node:
                leaves.append("{} :: {} / {} : {}".format(node.path, node.count.numerator, node.count.denominator, node._example))
            else:
                queue += list(node.data.values())

        return leaves

    def convert_to_rational(self, total_count):
        if not isinstance(self.count, Fraction):
            self.count = Fraction(self.count, total_count)
        total_count = sum([x.count for x in self.data.values()])
        for x in self.data.values():
            x.convert_to_rational(total_count)


    def construct_likely_path(self):
        path = ""
        current = self
        while bool(self):
            children = list(self.data.values())
            prob_pairs = [(x.count, x) for x in children]

            #random selection
            current = prob_pairs[0][1]
            path += " {} ({}) ".format(current.key, str(current.count))

        return path



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

def xml_search_components(data, soup, initial):
    """ Summarize a file's tags and attributes, hierarchically """
    queue = set(initial)
    handled = set()
    while bool(queue):
        logging.info("Queue len: {}".format(len(queue)))
        current = queue.pop()
        if current is None or current in handled:
            continue
        handled.add(current)
        sub_components = list({y.name for x in soup.find_all(current) for y in x.contents if y.name is not None})
        attrs = set([x for y in soup.find_all(current) for x in y.attrs.keys()])
        queue.update(sub_components)
        data['components_{}'.format(current)] = sub_components
        if bool(attrs):
            data['attrs_{}'.format(current)] = attrs

    return data
