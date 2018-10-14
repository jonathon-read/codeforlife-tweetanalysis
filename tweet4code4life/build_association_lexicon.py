#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import Counter
import os
import sqlite3
from tqdm import tqdm


def _count_cooccurrences(docs, threshold=4):

    # count all cooccurrences in docs
    unfiltered = dict()
    for doc in tqdm(docs, desc='counting cooccurrences'):
        doc = [feature.strip() for feature in doc]
        doc = set([feature for feature in doc if len(feature) > 0])
        for feature in doc:
            try:
                y = unfiltered[feature]
            except KeyError:
                y = Counter()
                unfiltered[feature] = y
            y.update(doc)

    # filter infrequent instances
    filtered = dict()
    for feature, cooccurrences in tqdm(unfiltered.items(), desc='filtering infrequent instances'):
        cooccurrences = {cooccurrer: frequency
                         for cooccurrer, frequency in cooccurrences.items()
                         if frequency > threshold}
        if cooccurrences:
            filtered[feature] = cooccurrences

    return filtered


def count_coocurrences(source_paths):
    cooccurrences = dict()
    for source_path in source_paths:
        with open(source_path, 'rt') as file_obj:
            for line in file_obj:
                features = [feature for feature in [feature.strip() 
                                                    for feature in line.split('\t')] \
                            if len(feature) > 0]
                features = 



def main():

    parser = ArgumentParser(description='Tweet 4 Code 4 Life lexicon building')
    parser.add_argument('source', nargs='+')
    parser.add_argument('--threshold', default=4)
    args = parser.parse_args()

    cooccurrences = count_cooccurrences(args.source)
    

def main_cooc_list(args):
    cursor = _db.cursor()
    cursor.execute(_sql['get_cooccurrences'], {'entry': args.entry})
    for cooccurrer, frequency in cursor:
        print(cooccurrer, frequency)


def main_cooc_update(args):

    docs = list()
    for source in args.source:
        with open(source, 'rt') as file_obj:
            docs.extend([line.split('\t') for line in file_obj])

    cooccurrences = _count_cooccurrences(docs)

    cursor = _db.cursor()

    # add new entries to the database
    cursor.executemany(_sql['add_new_entries'], [{'entry': entry} for entry in cooccurrences.keys()])
    _db.commit()

    # get all entry identifiers
    cursor.execute(_sql['get_all_entries'])
    entry_ids = {entry: entry_id for entry_id, entry in cursor.fetchall()}

    # record cooccurrences
    cooccurrence_updates = list()
    for entry_a, a_cooccurrences in tqdm(cooccurrences.items()):
        entry_a = entry_ids[entry_a]
        for entry_b, frequency in a_cooccurrences.items():
            entry_b = entry_ids[entry_b]
            if entry_a is entry_b:
                cursor.execute(_sql['update_occurrences'], {'entry_id': entry_a,
                                                            'frequency': frequency})
            else:
                cooccurrence_updates.append({
                    'entry_a': entry_a,
                    'entry_b': entry_b,
                    'frequency': frequency
                })
    cursor.executemany(_sql['update_cooccurrences'], cooccurrence_updates)
    _db.commit()


def main_freq(args):
    cursor = _db.cursor()
    cursor.execute(_sql['get_frequency'], {'entry': args.entry})
    frequency = cursor.fetchone()
    print(0 if frequency is None else frequency[0])


def main_score_pmi(args):
    scores_to_set = list()
    cursor = _db.cursor()
    cursor.execute(_sql['get_scoring_input'])
    for entry_a, frequency_a, entry_b, frequency_b, frequency_ab in cursor:
        pmi



def main_truncate(args):
    cursor = _db.cursor()
    cursor.execute('DELETE FROM scores')
    cursor.execute('DELETE FROM cooccurrences')
    cursor.execute('DELETE FROM occurrences')
    cursor.execute('DELETE FROM entries')
    _db.commit()


if __name__ == '__main__':
    main()