#!/usr/bin/env python3
import logging as root_logger
logging = root_logger.getLogger(__name__)

from code_analysis.util.parse_state import ParseState

def handle_dota_patch_notes(data, soup):

    # TODO verify dota parsing
    # TODO use dota parsing
    # TODO create timeline from dota
    data['release_date'] = soup.find(id="firstHeading").text
    body_content = soup.find(id="bodyContent")
    initial_heading = body_content.find("h1")

    queue = initial_heading.parent.find_all(recursive=False)
    state = ParseState()
    # state = { 'current' : [initial_heading],
    #           'contents' : [] }

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

def handle_df_patch_notes(data, soup):
    # TODO verify release info parse
    # TODO create timeline
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
