import os
import itertools
from abc import ABCMeta, abstractmethod, abstractproperty

import pandas as pd


class FramewiseData(object):

    __metaclass__ = ABCMeta

    @abstractmethod
    def write(self, df):
        pass

    @abstractmethod
    def read(self, frame_no):
        pass

    @abstractmethod
    def __iter__(self):
        pass

    @abstractproperty
    def t_column(self):
        pass

    def _validate(self, df):
        if self.t_column not in df.columns:
            raise ValueError("Cannot write frame without a column "
                             "called {0}".format(self.t_column))


class PandasHDFStore(FramewiseData):

    def __init__(self, filename, key, t_column='frame',
                 use_tabular_copy=False):
        self.filename = os.path.abspath(filename)
        self.key = key
        self._t_column = t_column

        with pd.get_store(self.filename) as store:
            try:
                store[self.key]
            except KeyError:
                pass
            else:
                self._validate_node(use_tabular_copy)

    @property
    def t_column(self):
        return self._t_column

    def write(self, df):
        self._validate(df)
        with pd.get_store(self.filename) as store:
            store.append(self.key, df, data_columns=True)

    def read(self, frame_no):
        with pd.get_store(self.filename) as store:
            frame = store.select(self.key, 'frame == %d' % frame_no)
        return frame

    def __iter__(self):
        return self._build_generator()

    def _build_generator(self):
        with pd.get_store(self.filename) as store:
            for frame_no in self._inspect_frames():
                frame = store.select(self.key, 'frame == %d' % frame_no)
                if len(frame) == 0:
                    continue  # Do not yield this; try the next frame no.
                yield frame

    def _inspect_frames(self):
        # For now, just try starting at 0.
        return itertools.count(0)

    def _validate_node(self, use_tabular_copy):
        # The HDFStore might be non-tabular, which means we cannot select a 
        # subset, and this whole structure will not work.
        # For convenience, this can rewrite the table into a tabular node.
        if use_tabular_copy:
            self.key = _make_tabular_copy(self.filename, self.key)

        with pd.get_store(self.filename) as store:
            pandas_type = getattr(getattr(getattr(
                store._handle.root, self.key, None), '_v_attrs', None), 
                'pandas_type', None)
        if not pandas_type == 'frame_table':
            raise ValueError("This node is not tabular. Call with "
                             "use_tabular_copy=True to proceed.")


def _make_tabular_copy(filename, key):
    """Copy the contents nontabular node in a pandas HDFStore
    into a tabular node"""
    tabular_key = key + '/tabular'
    print "Making a tabular copy of %s at %s" % (key, tabular_key)
    with pd.get_store(filename, 'w') as store:
        store.append(tabular_key, store.get(key), data_columns=True)
    return tabular_key
