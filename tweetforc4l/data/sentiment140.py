#!/usr/bin/env python3

import logging
import os
import pandas as pd
import ssl
from urllib.request import urlretrieve
from tqdm import tqdm
from zipfile import ZipFile

from tweetforc4l.data.preprocessing import classify_language, SpacyCache


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_LOCAL_PATH = 'data/sentiment140'
_TRAINING_CSV = 'training.1600000.processed.noemoticon.csv'
_ARCHIVE_COLUMNS = ['target', 'id', 'date', 'flag', 'user', 'primary']
_URL = 'http://cs.stanford.edu/people/alecmgo/trainingandtestdata.zip'

os.makedirs(_LOCAL_PATH, exist_ok=True)


def get_archive():
    path_to_archive = os.path.join(_LOCAL_PATH, 'archive.zip')
    if os.path.exists(path_to_archive):
        logging.info('archive already downloaded, reusing %s', path_to_archive)
    else:
        ssl._create_default_https_context = ssl._create_unverified_context
        urlretrieve(_URL, path_to_archive)
        logging.info('archive downloaded from %s', _URL)
    return path_to_archive


def extract_primary_data(path_to_archive):
    with ZipFile(path_to_archive) as zip_file:
        df = pd.read_csv(zip_file.open(_TRAINING_CSV),
                         encoding='latin1',
                         names=_ARCHIVE_COLUMNS)
        df['sentiment'] = df['target'].map({0: 'negative',
                                            2: 'neutral',
                                            4: 'positive'})
        logging.info('extracted primary data, %d tweets found', len(df))
        return df[['sentiment', 'user', 'primary']]


def main():
    df = extract_primary_data(get_archive())
    logging.info('extracted primary data')
    df['langid'] = classify_language(df['primary'])
    df = df[df['langid'] == 'en'].reindex()
    df.to_csv(os.path.join(_LOCAL_PATH, 'primary.csv'), index=True)

    spacy_cache = SpacyCache(root=os.path.join(_LOCAL_PATH, 'spacy'))
    docs = list(tqdm(spacy_cache.get(df['primary']), total=len(df)))
    spacy_cache.finalise()


if __name__ == '__main__':
    main()
