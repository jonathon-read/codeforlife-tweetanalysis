
import dask
import dask.dataframe
import dask.diagnostics
import dask.multiprocessing
import langid
import os
import pickle
import spacy
from spacy.tokens import Doc


def classify_language(texts):
    dd = dask.dataframe.from_pandas(texts.to_frame(), npartitions=100)
    with dask.diagnostics.ProgressBar():
        return dd.map_partitions(
            lambda df: df.apply(
                (lambda row: langid.classify(row['primary'])[0]), axis=1)) \
            .compute(get=dask.multiprocessing.get)


class SpacyCache(object):

    def __init__(self, root, model=None):

        self._contents = dict()
        self._root = root

        model_path = os.path.join(self._root, 'model.txt')
        if model:
            if os.path.exists(model_path):
                raise ValueError('model specified but %s already exists', model_path)
            else:
                self._model = model
                with open(model_path, 'wt') as handle:
                    handle.write(model)
        else:
            with open(model_path, 'rt') as handle:
                self._model = handle.read()

        self._nlp = spacy.load(self._model)

        try:
            with open(os.path.join(self._root, 'vocab.pickle'), 'rb') as handle:
                self._nlp.vocab.from_bytes(pickle.load(handle))
        except FileNotFoundError:
            pass

    def finalise(self):
        with open(os.path.join(self._root, 'vocab.pickle'), 'wb') as handle:
            pickle.dump(self._nlp.vocab.to_bytes(), handle)

    def get(self, texts, n_threads=-1):

        identifiers_todo = list()
        texts_todo = list()
        for identifier, text in texts.iteritems():
            try:
                yield identifier, self._contents[identifier]

            except KeyError:

                try:
                    doc = self._load(identifier)
                    self._contents[identifier] = doc
                    yield identifier, doc

                except FileNotFoundError:
                    identifiers_todo.append(identifier)
                    texts_todo.append(text)

        if texts_todo:
            docs = self._nlp.pipe(texts_todo, n_threads=n_threads)
            for identifier, doc in zip(identifiers_todo, docs):
                self._save(identifier, doc)
                self._contents[identifier] = doc
                yield identifier, doc

    def _get_path(self, identifier):
        identifier = '{:07d}'.format(identifier)
        subset = os.path.join(self._root, 'docs', identifier[:4])
        os.makedirs(subset, exist_ok=True)
        return os.path.join(subset, '{}.pickle'.format(identifier))

    def _load(self, identifier):
        with open(self._get_path(identifier), 'rb') as handle:
            doc_bytes = pickle.load(handle)
        return Doc(self._nlp.vocab).from_bytes(doc_bytes)

    def _save(self, identifier, doc):
        with open(self._get_path(identifier), 'wb') as handle:
            pickle.dump(doc.to_bytes(), handle)