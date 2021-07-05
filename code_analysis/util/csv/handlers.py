#!/usr/bin/env python3
def handle_BBC(rows):
    data = { 'base_url' : 'http://bbcsfx.acropolis.org.uk/assets/{}',
             'sounds' : [],
             'categories' : set(),
    }
    for row in rows:
        data['categories'].add(row['category'])
        data['sounds'].append({
            'url' : row['location'],
            'desc' : row['description'],
            'len' : row['secs'],
            'tag' : row['category']
            })

    return data

def handle_DAMSL(rows):
    data = {
        'meta' : [],
        'statements': []
    }
    keys = [x for x in rows[0].keys()]
    in_meta = False
    if 'swda_filename' not in keys:
        in_meta = True

    # TODO stats on utterances
    # TODO stats on call,response and balance of conv
    for row in rows:
        if in_meta:
            data['meta'].append({
                'topic' : row['topic_description'],
                'conv_id' : row['conversation_no'],
                'genders' : [row['from_caller_sex'],row['to_caller_sex']]
            })
        else:
            data['statements'].append({
                'conv_id' : row['conversation_no'],
                'transcript_index' : "{}.{}.{}".format(row['transcript_index'],
                                                       row['utterance_index'],
                                                       row['subutterance_index']),
                'speech_act_tag' : row['act_tag'],
                'caller' : row['caller'],
                'text' : row['text']
                })

    return data

def handle_StopAndFrisk(rows):
    data = {}
    # TODO handle_ stop and frisk data
    return data

def handle_Badge(rows):
    data = {}
    # TODO handle_ badge data
    return data

def handle_dialogue(text):
    data = {}
    csv_obj = csv.reader(text, delimiter="\t", quotechar='"')

    rows = [x for x in csv_obj]

    variables = list(set([y[0] for x in rows for y in re.findall("%(\w+)(\([\w,]*\))?%", x[0])]))

    data['length'] = len(rows)
    data['speech_acts'] = list(set([y for x in rows for y in x[1].split(',') if bool(y)]))
    data['num_speech_acts'] = len(data['speech_acts'])
    data['variables'] = variables

    # TODO parse text?

    return data
