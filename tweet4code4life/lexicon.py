#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import Counter
import pandas as pd
import yaml

with open('config.yaml', 'rt') as handle:
    config = yaml.load(handle)


def build_cooccurrence_matrix(docs, threshold=4):

    # count all cooccurrences in docs
    unfiltered = dict()
    for doc in docs:
        doc = set(doc)
        for feature in doc:
            try:
                y = unfiltered[feature]
            except KeyError:
                y = Counter()
                unfiltered[feature] = y
            y.update(doc)

    # filter infrequent instances
    filtered = dict()
    for feature, cooccurrences in unfiltered.items():
        cooccurrences = {cooccurrer: frequency
                         for cooccurrer, frequency in cooccurrences.items()
                         if frequency > threshold}
        if cooccurrences:
            filtered[feature] = cooccurrences

    return pd.DataFrame(filtered)


def get_argument_parser():
    parser = ArgumentParser(description='Tweet 4 Code 4 Life lexicon management')
    subparsers = parser.add_subparsers()

    parser_cooc = subparsers.add('cooc', description='cooccurrences and things')
    parser_cooc.add_argument('function', choices=['get', 'update'])
    return parser


def main():
    args = get_argument_parser().parse_args()
    print(args)


if __name__ == '__main__':
    main()