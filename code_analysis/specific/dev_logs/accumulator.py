#!/usr/bin/env python3

def accumulator(new_data, accum_data, ctx):
    #accumulate all words to get frequencies
    for date,text in new_data.items():
        #TODO process dates

        #Accumulate text
        parsed = nlp(text)

        accum_data['__total_count'] += len(parsed)

        for sen in parsed.sents:
            # TODO create timeline of releases and features

            # Skip non-useful words
            for word in sen:
                if any([word.pos in [spacy.symbols.PUNCT, spacy.symbols.SPACE],
                        word.is_punct, word.is_space, word.is_stop]):
                    continue

                # accumulate lemmas
                word_lemma = word.lemma_.lower()
                if word_lemma not in accum_data:
                    accum_data['__unique_words'].add(word_lemma)
                    accum_data[word_lemma] = 0
                accum_data[word_lemma] += 1

            # count sentence lengths
            if len(sen) not in accum_data['__sen_counts']:
                accum_data['__sen_counts'][len(sen)] = 0
            accum_data['__sen_counts'][len(sen)] += 1

    return accum_data

def accumulator_final(data, ctx):
    #once accumulated, normalize?

    return data
