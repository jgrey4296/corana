#!/usr/bin/env python3
from code_analysis.util.parse_base import ParseBase

class NYT_Entry(ParseBase):

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
