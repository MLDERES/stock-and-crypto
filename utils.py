import math
from dateutil.relativedelta import  relativedelta
import numpy as np
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
from pathlib import Path
import datetime as dt

ALPHA_API = 'L9PC2T5MJKB9QSAL'
OPEN_PRICE = 'open'
DAY_HIGH = 'high'
DAY_LOW = 'low'
DAY_CLOSE = 'close'
ADJ_CLOSE = 'adjusted close'
DAY_VOLUME = 'volume'
DIVIDEND_AMT = 'dividend amt'
SPLIT_COEFFICIENT = 'split coef'
MARKET_CAP = 'market cap'
FALSE_VALUES = ['No', 'no', 'n', 'N','F','False', 'FALSE']
TRUE_VALUES = ['Yes', 'yes', 'y', 'Y','T','True','TRUE']
DATA_PATH = Path('./data')
TODAY = pd.datetime.today()

def get_latest_file(file_path, filename_like, file_ext):
    """
    Find absolute path to the file with the latest timestamp given the datasource name and file extension in the path
    :param file_path: where to look for the file
    :param filename_like: the basename of the datafile.  For instance if the datasource_name is foo then the filename
          representing the latest modified file with a name like 'foo*' will be returned
    :param file_ext: the filename extension
    :return: the absolute path to the file
    """
    file_ext = file_ext if '.' in file_ext else f'.{file_ext}'
    all_files = [f for f in file_path.glob(f'{filename_like}*{file_ext}', )]
    assert len(all_files) > 0, f'Unable to find any files like {file_path / filename_like}{file_ext}'
    fname = max(all_files, key=lambda x: x.stat().st_mtime).name
    return fname

def read_latest(datasource_name, errors='raise', **kwargs):
    """
    Get the most recent version of the cleaned dataset
    :param datasource_name: name of the file to get the data from
    :param errors: if 'raise' then
    :return:
    """
    read_path = DATA_PATH
    try:
        fname = get_latest_file(read_path, datasource_name, ".csv")
        ret_df = pd.read_csv(read_path / fname, index_col=0, infer_datetime_format=True, true_values=TRUE_VALUES,
                       false_values=FALSE_VALUES, **kwargs)
    except AssertionError:
        ret_df = None
        if errors != 'ignore':
            raise
    finally:
        return ret_df
    
def write_data(df, datasource_name, with_ts=True, **kwargs):
    """
    Export the dataset to a file
    :param df: the dataset to write
    :param datasource_name: the base filename to write
    :param with_ts: if True, then append the year, month, day and hour to the filename to be written
                    else append the suffix 'latest' to the basename
    :param idx: the name of the index or the column number
    :return: the name of the file written
    """
    NOW = dt.datetime.now()
    fn = make_ts_filename(DATA_PATH, src_name=datasource_name, suffix='.csv', with_ts=with_ts)

    if 'float_format' not in kwargs.keys():
        kwargs['float_format'] = '%.3f'
    df.to_csv(fn, **kwargs)
    return fn


def make_ts_filename(dir_name, src_name, suffix, with_ts=True):
    """
    Get a path with the filename specified by src_name with or without a timestamp, in the appropriate directory
    :param dir_name:
    :param src_name:
    :param suffix:
    :param with_ts:
    :return:
    """
    NOW = dt.datetime.now()
    TODAY = dt.datetime.today()
    filename_suffix = f'{TODAY.month:02d}{TODAY.day:02d}_{NOW.hour:02d}{NOW.minute:02}{NOW.second:02d}' \
        if with_ts else "latest"
    fn = f'{src_name}_{filename_suffix}'
    suffix = suffix if '.' in suffix else f'.{suffix}'
    filename = (dir_name / fn).with_suffix(suffix)
    return filename