#!/usr/bin/env python3
from provenance.util.parse_state import ParseState

def parse_wow_quest(data, soup):
    logging.info("Parsing Wow Quest")
    data = {}

    wikiapage = soup.find(id="WikiaPage")
    assert(wikiapage is not None)
    data['title'] = wikiapage.find("h1").text

    main_container = wikiapage.find(id="mw-content-text")
    assert(main_container is not None)
    # Get the side box
    aside = main_container.find("aside")
    if aside is not None:
        aside_details = aside.find_all("div",class_="pi-item")
        for detail in aside_details:
            pair = detail.findChildren(recursive=False)
            assert(len(pair) >= 2)
            data[pair[0].text] = [x.get_text(", ") for x in pair[1:]]

    # Main content:
    content = [x for x in main_container.findChildren(recursive=False) if x.name in ["h2", "p", "table", "ul", "ol"]]
    #Get rid of cruft at the start
    while bool(content) and content[0].name != 'h2':
        content.pop(0)
    h2s = [x for x in content if x.name == "h2"]
    ids = [y.attrs['id'] for x in h2s for y in x.findChildren(recursive=False) if 'id' in y.attrs]

    #loop through content, assigning p's to h2s
    curr_section = None
    while bool(content):
        current = content.pop(0)
        if current.name == "h2":
            curr_section = current.find('span').text
            data[curr_section] = []
        elif current.name == "p":
            assert(curr_section is not None)
            data[curr_section].append(current.text)
        elif current.name == "ul":
            data[curr_section] += wow_handle_ul(current)
        elif current.name == "ol":
            data[curr_section].append(wow_handle_ol(current))
        elif current.name == "table":
            links = current.find_all('a')
            link_texts = [x.text for x in links if x.text != ""]
            data[curr_section].append(link_texts)
    return data


def wow_handle_ol(data, current):
    lis = current.find_all('li', recursive=False)
    result = []
    for li in lis:
        if li.find('ul'):
            li_contents = [x for x in [li.contents[0].strip()] if x != ""]
            li_contents += wow_handle_ul(li.find('ul'))
        else:
            li_contents = li.get_text()
        result.append(li_contents)

    return result

def wow_handle_ul(data, current):
    lis = current.find_all('li',recursive=False)
    result = []
    for li in lis:
        if li.find('ol'):
            ol_contents = [x for x in [li.contents[0].strip()] if x != ""]
            ol_contents += wow_handle_ol(li.find('ol'))
            result.append(ol_contents)
        else:
            text = li.get_text()
            img = li.find('img')
            if img and 'alt' in img.attrs:
                text += " {}".format(img.attrs['alt'])
            result.append(text)

    return result



def parse_trump(data, soup):
    data = {}

    posts = soup.find_all("article")
    data['_num_posts'] = len(posts)
    data['days_mentioned'] = []
    data['components'] = set()
    for post in posts:
        day = post.find('h2').find('a').attrs['href']
        logging.info("Processing post: {}".format(day))

        for sub_structure in post.findChildren():
            data['components'].add(sub_structure.name)

        data[day] = {}
        data[day]['date'] = post.find('time').attrs['datetime']
        data['days_mentioned'].append(data[day]['date'])

        paras = post.find_all('p', recursive=False)
        texts = [x.text for x in paras]
        data[day]['paragraphs'] = texts
        links = [y.attrs['href'] for x in paras for y in x.find_all('a')]
        data[day]['links'] = links

    return data


def parse_bible(data, soup):
    data = {}
    divs = soup.find_all('divs')

    for section in divs:
        book, testament, chapter, verse = KJV_RE.match(section.find(h1).string).groups()
        text = nlp(section.find('p').string)

        #TODO bible analysis

    return data


def parse_usc(data, soup):
    data = {}

    # describe and aggregate
    data.update(utils.xml_search_components(data, soup, ['main']))

    # TODO extract into groups, convert to text, parse
    # TODO extract deontics
    # TODO extract sanctions

    return data


def parse_king_dragon_pass(data, soup):
    data = {}

    #TODO extract structure

    return data


def parse_roberts_rules(data, soup):
    data = {}

    body = soup.find('body')
    contents = body.contents

    # TODO: discard up to first heading

    page_re = re.compile(r"^\s*=+ Page ([0-9]+)\s+=+\s*$")
    id_re = re.compile(r"id(\d+)")

    contents = []
    pages = {}
    index = []
    sections = {'0' : []}
    current_page = 0

    #range of contents
    contents_ids= [int(id_re(x)[1]) for x in ["id00033", "id00054"]]
    bullet_ids = [int(id_re(x)[1]) for x in ["id00076", "id00552", "id00554"]]
    list_ids = [int(id_re(x)[1]) for x in ["id00119", "id00124", "id00126", "id00220", "id00356"]]
    ignore_ids = [int(id_re(x)[1]) for x in ["id00692"]]
    index_ids = [int(id_re(x)[1]) for x in ["id00725", "id00741"]]

    while bool(contents):
        current = contents.pop(0)
        current_text = current.get_text()
        id_num = int(id_re.match(current.id)[1])
        if id_num in ignore_ids:
            continue

        # match pages
        is_page = page_re.match(current_text)
        if is_page:
            pages[int(is_page[1])] = []
            current_page = int(is_page[1])
        elif contents_ids[0] <= id_num <= contents_ids[1]:
            contents.append(current_text)
        elif id_num in bullet_ids:
            # TODO: deal with bullets
            continue
        elif id_num in list_ids:
            # TODO: deal with lists
            continue
        else:
            # split into pages
            pages[current_page].append(current_text)

        # TODO: recognise sections
        # TODO: recognise crossrefs


    return data


def parse_unrest(data, soup):
    data = {}

    #TODO extract structure


    return data
