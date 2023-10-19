"""
https://pygments.org/docs/lexerdevelopment/
"""
from __future__ import annotations
import pathlib as pl
import pygments
from pygments.lexer import RegexLexer
from pygments.formatter import Formatter
from pygments.formatters import HtmlFormatter
from pygments.filter import Filter
from pygments import token

# Comment, Error, Escape, Generic, Keyword, Literal, Name, Number,
# Operator, Other, Punctuation, STANDARD_TYPES, String, Text, Token, Whitespace,
#
# Generic: Deleted, Emph, Error, Heading, Inserted, Output, Prompt, Strong, Subheading, Traceback,

class TestLexer(RegexLexer):
    name      = "mytest"
    aliases   = ["mt"]
    filenames = ["*.jgt"]

    tokens = {
        # State : [ (ruleRegex, ruleToken|callback, nextState ]
        'root' : [
            (r'Head:.*\n', token.Generic.Heading),
            (r'Key:.*\n',  token.Keyword),
            (r'Lit:.*\n',  token.Literal),
            (r'Name:.*\n', token.Name),
            (r".*\n", token.Text),
        ]
    }

class TestFormatter(Formatter):

    def format(self, tokensource:Iterable[tuple], outfile):
        for ttype, value in tokensource:
            outfile.write(value)

class TestFilter(Filter):

    def filter(self, lexer, stream):
        for ttype, value in stream:
            yield ttype, value

def main():
    pl.Path("results.html").write_text(pygments.highlight(pl.Path("mytest.jgt").read_text(), TestLexer(), HtmlFormatter()))

    lex = pygments.lex(pl.Path("mytest.jgt").read_text(), TestLexer())
    pass
