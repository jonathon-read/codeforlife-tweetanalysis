#!/usr/bin/env python3

from argparse import ArgumentParser
import html
import langid
import os
import pandas as pd
import ssl
from tqdm import tqdm
from urllib.request import urlretrieve
import yaml
from zipfile import ZipFile

from features import get_lemmas, get_lemmas_with_pos


def download_archive(url, path_to_archive):

    with tqdm(desc='Downloading sentiment140 from {}'.format(url)) as progress:
        def report(_, block_size, total_size):
            progress.total = total_size
            progress.update(block_size)

        ssl.create_default_https_context = ssl._create_default_https_context
        urlretrieve(url, path_to_archive, reporthook=report)


def extract_data(internal_file, path_to_archive):
    with ZipFile(path_to_archive) as zip_file:
        df = pd.read_csv(zip_file.open(internal_file),
                         encoding='latin1', names=['target', 'id', 'date', 'flag', 'user', 'tweet'])
    df['sentiment'] = df['target'].map({0: 'negative',
                                        2: 'neutral',
                                        4: 'positive'})
    return df[['sentiment', 'user', 'tweet']]


def get_args():
    parser = ArgumentParser(description='Sentiment140 Tweet Dataset preprocessing')
    parser.add_argument('--data_dir', type=str, default='data', help='path to download directory')
    parser.add_argument('--features', type=str, required=True, help='type of features to extract',
                        choices={'lemmas', 'lemmas_pos'})
    parser.add_argument('--test_ratio', type=float, default=0.1, help='proportion of data to reserve for testing')
    return parser.parse_args()


def get_subsets(df, test_ratio):
    split_at = int(len(df) * test_ratio)
    train, test = df.iloc[:-split_at], df.iloc[-split_at:]
    return ('test', 'positive', test[test['sentiment'] == 'positive']),\
           ('test', 'negative', test[test['sentiment'] == 'negative']),\
           ('train', 'positive', train[train['sentiment'] == 'positive']),\
           ('train', 'negative', train[train['sentiment'] == 'negative'])


def main():

    with open('config.yaml') as file_obj:
        config = yaml.load(file_obj)['sentiment140']

    args = get_args()

    path_to_archive = os.path.join(args.data_dir, 'sentiment140.zip')
    if not os.path.exists(path_to_archive):
        download_archive(config['url'], path_to_archive)

    df = extract_data(config['training'], path_to_archive)
    df = df[~df.user.isin(config['robots'])]
    df = df.sample(frac=1.0, random_state=42)

    if args.features == 'lemmas':
        get_features = get_lemmas
    elif args.features == 'lemmas_pos':
        get_features = get_lemmas_with_pos

    feature_cache = dict()
    with open('{}.cache'.format(args.features), 'rt') as file_obj:
        for line in file_obj:
            tweet, features = line.split('§')
            feature_cache[tweet] = features

    cache_file_obj = open('{}.cache'.format(args.features), 'at')

    with tqdm(total=len(df)) as progress:
        for split, sentiment, subset_df in get_subsets(df, args.test_ratio):
            path = os.path.join(args.data_dir, '{}-{}-{}.tsv'.format(args.features, split, sentiment))
            progress.set_description(path)
            with open(path, 'wt') as file_obj:
                for tweet in subset_df['tweet'].values:

                    tweet = html.unescape(tweet)

                    if 'we.will.never.sleep.cause.sleep.' in tweet:
                        tweet = tweet.replace('.', ' ')

                    if langid.classify(tweet)[0] == 'en':
                        try:
                            features = feature_cache[tweet]
                        except KeyError:
                            features = '\t'.join(get_features(tweet))
                            feature_cache[tweet] = features
                            cache_file_obj.write('{}§{}\n'.format(tweet, features))
                            cache_file_obj.flush()
                        file_obj.write(features + '\n')
                    progress.update()

    cache_file_obj.close()







if __name__ == '__main__':
    main()