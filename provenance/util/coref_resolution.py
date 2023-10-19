import spacy
from textblob import TextBlob


def resolve_coreferences(text, candidates):
    """ Given a piece of text, resolve coreferences in it
    using Raghunathan et al 2010's multi-pass sieve method """
    mentions = []

    # TODO Perform candidate setup

    # TODO Perform each pass

    return mentions

def exact_match_pass(text, candidates):
    mentions = []
    return mentions

def precise_constructs_pass(text, candidates):
    mentions = []
    return mentions

def strict_head_pass(text, candidates):
    mentions = []
    return mentions

def strict_head_variant_pass(text, candidates):
    mentions = []
    return mentions

def relaxed_head_pass(text, candidates):
    mentions = []
    return mentions

def pronoun_pass(text, candidates):
    mentions = []
    return mentions
