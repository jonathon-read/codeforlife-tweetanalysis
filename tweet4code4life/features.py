
import logging
import spacy


_nlp = None
_spacy_model = 'en_core_web_lg'


def _spacy(text, disable=[]):

    global _nlp

    if _nlp is None:
        logging.info('loading spacy model {}'.format(_spacy_model))
        _nlp = spacy.load(_spacy_model)

    return _nlp(text, disable=disable)


def get_lemmas(text):
    features = list()
    for token in _spacy(text, disable=['parser', 'ner']):
        if token.lemma_.startswith('@'):
            features.append('__HANDLE__')
        elif 'http' in token.lemma_ or 'www' in token.lemma_:
            features.append('__URL__')
        else:
            features.append(token.lemma_)
    return features


def get_lemmas_with_pos(text):
    features = list()
    for token in _spacy(text, disable=['parser', 'ner']):
        if token.lemma_.startswith('@'):
            features.append('//'.join('__HANDLE__', 'PROPN'))
        elif 'http' in token.lemma_ or 'www' in token.lemma_:
            features.append('//'.join('__URL__', '__URL__'))
        else:
            features.append('//'.join(token.lemma_, token.tag_))
    return features
