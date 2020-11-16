"""
Get cif rules files from data dir,

output to similarly named files in analysis directory
"""

from enum import Enum
from os import listdir
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from random import shuffle
import csv
import pyparsing as pp
import re
import spacy

import src.util.analysis_case as AC
import src.util.utils as utils

#Choose:
#https://docs.python.org/3/library/xml.etree.elementtree.html
import lxml
from bs4 import BeautifulSoup


nlp = spacy.load("en_core_web_sm")
# Setup root_logger:
from os.path import splitext, split
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

def extract_from_file(filename):
    logging.info("Extracting from: {}".format(filename))
    data = { }

    with open(filename, 'rb') as f:
        text = f.read().decode('utf-8','ignore')

    soup = BeautifulSoup(text, features='lxml')

    # Handle File Type
    if soup.find('cifstate') is not None:
        data = extract_from_cifstate(soup)
        data['is_cifstate'] = True
    elif soup.find('promweek') is not None:
        data = extract_from_promweek(soup)
        data['is_promweek'] = True
    elif soup.find('ciflibraries') is not None:
        data = extract_from_cif_library(soup)
        data['is_cif_library'] = True

    return data

def extract_from_cif_library(soup):
    data = {}
    contents = soup.find('ciflibraries')
    data['cif_library_contents'] = list({x.name for x in contents if x.name is not None})

    # data = utils.xml_search_components(data, soup, data['cif_library_contents'])
    cif_library_components = {'responderinfluenceruleset', 'initiatorinfluenceruleset', 'performancerealization', 'name', 'conditionalrules', 'conditionrule', 'effect', 'instantiations', 'definition', 'instantiation', 'rule', 'influencerule', 'preconditions', 'changerule', 'toc2', 'partialchange', 'toc3', 'lineofdialogue', 'patsyrule', 'intents', 'effects', 'toc1', 'microtheory', 'chorusrule', 'predicate', 'socialgame'}
    data['all_counts'] = {x : len(soup.find_all(x)) for x in cif_library_components}

    #get all predicates of rules/chorusRules/partialChanges/intents/changeRules/conditionRules/influenceRules
    # TODO  predicate_attrs : second, window, first, intent, trait, numtimesroleslot,
    # TODO  numtimesuniquelytrueflag, value, networktype, issfdb, relationship, label,
    # TODO  type, comparator, negated, status, numtimesuniquelytrue predicates =
    predicates = contents.find_all('predicate')

    data['all_predicates'] = [str(x) for x in predicates]

    #get all performance realizations
    performances = contents.find_all('performancerealization')
    data['all_performances'] = [x.string for x in performances]

    # TODO influence rules have weights.


    return data

def extract_from_cifstate(soup):
    data = {}
    contents = soup.find('cifstate')
    data['cif_state_contents'] = list({x.name for x in contents if x.name is not None})

    # data = utils.xml_search_components(data, soup, data['cif_state_contents'])
    cif_state_components = {'trait', 'status', 'conditionrule', 'rule', 'relationship', 'character', 'backstorycontext', 'performancerealization', 'edge', 'proposition', 'changerule', 'predicate', 'locution', 'trigger'}
    data['all_counts'] = {x : len(soup.find_all(x)) for x in cif_state_components}

    # TODO sfdb, culturalkd,

    # TODO relationships
    # TODO network edges

    # TODO cast / locutions, traits, statuses


    return data

def extract_from_promweek(soup):
    data = { }
    contents = soup.find('promweek')
    data['prom_week_contents'] = list({x.name for x in contents if x.name is not None})

    # data = utils.xml_search_components(data, soup, data['prom_week_contents'])
    prom_week_components = {'endings', 'todorule', 'forcedsgs', 'todoitems', 'todolist', 'conditionalrules', 'tidbit', 'quickplayendingdescription', 'cast', 'goalrules', 'description', 'tasknaturallanguage', 'instantiations', 'levels', 'rule', 'goaldescription', 'instantiation', 'todoitem', 'preconditions', 'level', 'toc2', 'partialchange', 'setting', 'forcedsg', 'toc3', 'lineofdialogue', 'condition', 'toc1', 'chorusrule', 'charactername', 'predicate', 'quickplaydescription', 'ending'}
    data['all_counts'] = {x : len(soup.find_all(x)) for x in prom_week_components}

    # TODO todoitem : tidbit, condition, goaldescrptions

    # TODO level : setting, description, goalrules, cast

    # TODO ending : instantiation, preconditions

    return data


def accumulator(new_data, acc_data):
    #accumulator descriptions for cifstates, promweeks and ciflibraries

    if 'is_cifstate' in new_data:
        app_keys = [x for x in new_data.keys() if '_components' in x]
        acc_data['_cif_state_components'].update([y for x in app_keys for y in new_data[x]])
        for x in new_data['all_counts'].keys():
            if x not in acc_data['_cif_state_counts']:
                acc_data['_cif_state_counts'][x] = 0
            if x not in acc_data['__all_counts']:
                acc_data['__all_counts'][x] = 0
            acc_data['__all_counts'][x] += new_data['all_counts'][x]
            acc_data['_cif_state_counts'][x] += new_data['all_counts'][x]

    elif 'is_promweek' in new_data:
        app_keys = [x for x in new_data.keys() if '_components' in x]
        acc_data['_prom_week_components'].update([y for x in app_keys for y in new_data[x]])
        for x in new_data['all_counts'].keys():
            if x not in acc_data['_prom_week_counts']:
                acc_data['_prom_week_counts'][x] = 0
            if x not in acc_data['__all_counts']:
                acc_data['__all_counts'][x] = 0
            acc_data['__all_counts'][x] += new_data['all_counts'][x]
            acc_data['_prom_week_counts'][x] += new_data['all_counts'][x]

    elif 'is_cif_library' in new_data:
        app_keys = [x for x in new_data.keys() if '_components' in x]
        acc_data['_cif_library_components'].update([y for x in app_keys for y in new_data[x]])
        for x in new_data['all_counts'].keys():
            if x not in acc_data['_cif_library_counts']:
                acc_data['_cif_library_counts'][x] = 0
            if x not in acc_data['__all_counts']:
                acc_data['__all_counts'][x] = 0
            acc_data['__all_counts'][x] += new_data['all_counts'][x]
            acc_data['_cif_library_counts'][x] += new_data['all_counts'][x]

    return acc_data

def accum_final(data):


    return data

if __name__ == "__main__":
    queue = join("data","xml","CiFStates")
    input_ext = ".xml"
    output_lists = []
    output_ext = ".xml_rule_analysis"

    initial_accum = {'_cif_state_components': set(),
                     '_prom_week_components' : set(),
                     '_cif_library_components' : set(),

                     '_cif_state_counts': {},
                     '_prom_week_counts' : {},
                     '_cif_library_counts' : {},
                     '__all_counts' : {}
    }

    AC.AnalysisCase(queue,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext,
                    accumulator=accumulator,
                    accumulator_final=accum_final,
                    init_accum=initial_accum)()
