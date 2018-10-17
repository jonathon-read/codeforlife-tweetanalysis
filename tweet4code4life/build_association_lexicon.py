#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import Counter
import pandas as pd
import numpy as np


def count_features(source_paths):

    frequencies = Counter()
    joint_frequencies = dict()
    N = 0

    for source_path in source_paths:
        with open(source_path, 'rt') as file_obj:
            for tweet in file_obj:

                N += 1

                features = [feature.strip() for feature in tweet.split('\t')]
                features = set([feature for feature in features if len(feature) > 0])

                frequencies.update(features)

                for feature in features:

                    try:
                        counter = joint_frequencies[feature]
                    except KeyError:
                        counter = Counter()
                        joint_frequencies[feature] = counter

                    counter.update(features - set([feature]))

    return frequencies, joint_frequencies, N


def filter_infrequent_instances(unfiltered, threshold=4):
    filtered = dict()
    for feature, cooccurrences in unfiltered.items():
        cooccurrences = {cooccurrer: frequency
                         for cooccurrer, frequency in cooccurrences.items()
                         if frequency > threshold}
        if cooccurrences:
            filtered[feature] = cooccurrences
    return filtered


def pmi(pr_a, pr_b, pr_ab):
    return np.log(pr_ab) - (np.log(pr_a) + np.log(pr_b))


def pmi(a, b, frequencies, joint_frequencies, N):

    def pr(instances):
        return (instances + 1) / (N + len(frequencies))

    pr_a = pr(frequencies.loc[a])
    pr_b = pr(frequencies.loc[b])
    pr_ab = pr(joint_frequencies.loc[a][b])

    return np.log(pr(joint_frequencies[a][b])) - \
           (np.log(pr(frequencies.loc[a] + pr(frequencies.loc[b]))))

                    





def main():

    parser = ArgumentParser(description='Tweet 4 Code 4 Life lexicon building')
    parser.add_argument('source', nargs='+')
    parser.add_argument('--threshold', default=4)
    args = parser.parse_args()

    frequencies, joint_frequencies, N = count_features(args.source)
    joint_frequencies = filter_infrequent_instances(joint_frequencies)

    print(pmi('good', 'happy',))

    # frequencies = pd.DataFrame.from_dict(frequencies, orient='index', columns=['frequency'])
    # joint_frequencies = pd.DataFrame(joint_frequencies)




if __name__ == '__main__':
    main()