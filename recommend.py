import sys
import os
import re
import sys
import pandas as pd
from pandas import DataFrame


def main(argv):
    if len(argv) < 3:
        print('Usage: python recommend.py FILE_NAME PREDICATOR')
        sys.exit(1)

    file_name = argv[1]
    predicator = argv[2]

    data = read_csv(file_name)
    data['total_price'] = data['price'] + data['shipping'] - data['point']
    data = show_recommend(data, predicator)
    write_csv('rec_' + file_name, data)


def show_recommend(data: DataFrame, predicator: str):
    conditions = predicator.split(' and ')
    for condition in conditions:
        if re.search(r' > ', condition):
            column, value = condition.split(' > ')
            data = data[data[column].astype(float) > float(value)]
        elif re.search(r' < ', condition):
            column, value = (condition.split(' < '))
            data = data[data[column].astype(float) < float(value)]
        else:
            data = data.sort_values(condition)
    return data


def read_csv(file_name: str):
    file_path = os.path.join(os.getcwd(), file_name)
    if not os.path.exists(file_path):
        print("{} doesn't exist".format(file_name))
        sys.exit(1)

    with open(file_path, 'r') as f:
        df = pd.read_csv(f)
        return df


def write_csv(file_name: str, df: DataFrame):
    file_path = os.path.join(os.getcwd(), file_name)
    df.to_csv(file_path)


if __name__ == '__main__':
    main(sys.argv)