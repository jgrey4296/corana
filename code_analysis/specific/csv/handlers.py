#!/usr/bin/env python3
def handleBBC(rows):
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

def handleDAMSL(rows):
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

def handleDemocracy(rows, filename):
    data = {}

    # Assign file type
    d3t = DTYPE.NONE
    if "achievement" in filename:
        d3t = DTYPE.ACHIEVEMENT
    elif "policies" in filename:
        d3t = DTYPE.POLICY
    elif "policygroups" in filename:
        d3t = DTYPE.POLICYGROUP
    elif "pressuregroups" in filename:
        d3t = DTYPE.PRESSUREGROUP
    elif "simulation" in filename:
        d3t = DTYPE.SIMULATION
    elif "situations" in filename:
        d3t = DTYPE.SITUATION
    elif "sliders" in filename:
        d3t = DTYPE.SLIDER
    elif "votertypes" in filename:
        d3t = DTYPE.VOTER

    if d3t is DTYPE.ACHIEVEMENT:
        continue
    elif d3t is DTYPE.POLICY:
        # collect guinames, description
        # collect introduce, cancel, raise, lower, mincost, maxcost
        continue
    elif d3t is DTYPE.POLICYGROUP:
        # collect names
        continue
    elif d3t is DTYPE.PRESSUREGROUP:
        # group by type, get names and their group (includes remaining)
        # collect threat level texts
        # collect radicalisation and de-radical rates
        continue
    elif d3t is DTYPE.SIMULATION:
        # collect names, description, zone
        # min, default, max triples
        # count emotions
        # formulas : [y for x in rows for y in x['remaining'] if y not in ['#','']]]
        continue
    elif d3t is DTYPE.SITUATION:
        # needs resetting to original from game
        # collect names
        continue
    elif d3t is DTYPE.SLIDER:
        # collect names, group by discrete type
        # collect values
        continue
    elif d3t is DTYPE.VOTER:
        # collect guinames, plural pairs
        # collect descriptions
        # collect influences / remaining
        continue


    return data

def handleStopAndFrisk(rows):
    data = {}
    # TODO handle stop and frisk data
    return data

def handleBadge(rows):
    data = {}
    # TODO handle badge data
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
