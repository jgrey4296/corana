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

import analysis_case as AC
import utils

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

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = {}
    soup = None
    with open(filename,'rb') as f:
        text = f.read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(text, features='lxml')

    assert(soup is not None)
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}

    if "dota" in filename:
        data = extract_from_dota_patch_notes(soup)
    else:
        data = extract_from_release_info(soup)

    return data

def extract_from_dota_patch_notes(soup):
    data = { }

    # TODO verify dota parsing
    # TODO use dota parsing
    # TODO create timeline from dota
    data['release_date'] = soup.find(id="firstHeading").text
    body_content = soup.find(id="bodyContent")
    initial_heading = body_content.find("h1")

    queue = initial_heading.parent.find_all(recursive=False)
    state = { 'current' : [initial_heading],
              'contents' : [] }

    for elem in queue:
        if elem is None or elem.name is None or elem.text == "":
            continue

        if elem.name in ['h1','h2','h3']:
            if bool(state['contents']):
                key = "_".join([x.text for x in state['current']])
                data[key] = state['contents']
                state['current'] = [elem]
                state['contents'] = []
            else:
                state['current'].append(elem)
            continue

        # List Handling:
        try:
            if elem.name == "ul":
                # TODO: if contains ul, remove ul, get preface text, get text of ul, combine
                list_elements = [x for x in elem.find_all("li") if not x.find_all("ul")]
                available = [x.get_text().strip() for x in list_elements if x != "\n"]
                state['contents'] += [x for x in available if x != ""]
            elif elem.get_text().strip() != "":
                state['contents'].append(elem.get_text().strip())
        except Exception as e:
            breakpoint()

    key = "_".join([x.text for x in state['current']])
    data[key] = state['contents']

    return data

def extract_from_release_info(soup):
    # TODO verify release info parse
    # TODO create timeline
    data = {}
    title = soup.find('h1')
    release_date = soup.find('p')
    blockquote = soup.find('blockquote')

    headings = soup.find_all('h2')
    queue = headings[:]
    # Handle queue of headings
    while bool(queue):
        current = queue.pop(0)
        if current.find_next_sibling('ul') is None:
            continue
        curr_string = current.string
        if curr_string is None:
            curr_string = current.get_text()
        curr_string = curr_string.replace("[edit]","")
        data[curr_string] = [x for x in current.find_next_sibling('ul').strings if re.match('\n',x) is None]

    data['version'] = title.string

    release_match = None
    if release_date is not None:
        release_match = re.search('was released on (.+?)\.', release_date.get_text())

    if release_match is not None:
        release_string = release_match.group(1)
    else:
        release_string = "UNKNOWN"

    data['release_date' ] = release_string

    if blockquote is not None:
        the_string = blockquote.get_text().replace('\n',' ')
        data['release_quote' ] = the_string

    return data


if __name__ == "__main__":
    input_ext = ".html"
    output_lists = []
    output_ext = ".patch_notes_analysis"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
