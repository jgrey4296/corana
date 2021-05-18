#!/usr/bin/env python3

def handle_html_dev_log(soup, data):
    dev_list = soup.find('ul')

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
