from typing import List
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import sys
import os
import json
import csv


def main(argv):
    if len(argv) != 2:
        print('Please specify json file which defines parameters')
        sys.exit(1)

    params = read_param(argv[1])
    results = scrape(params)
    save_to_csv(get_save_file_name(params), results)


def read_param(json_file: str) -> dict:
    file_path = os.path.join(os.getcwd(), json_file)

    if not os.path.exists(file_path):
        print("Json file doesn't exist")
        sys.exit(1)

    with open(file_path) as f:
        print('Reading parameters from {}'.format(file_path))
        params = json.load(f)
        return params


def scrape(params: dict) -> list:
    print('scraping with {}'.format(params))

    options = Options()
    options.add_argument('--headless')
    browser = webdriver.Chrome(options=options)

    keyword = params.pop('keyword')
    get_params = ''
    for key, value in params.items():
        key_value = '{}={}'.format(key, value)
        if not get_params:
            get_params = key_value
        else:
            get_params = '{}&{}'.format(get_params, key_value)
    url = 'https://search.rakuten.co.jp/search/mall/{}/?{}'.format(
        keyword, get_params)

    results = []

    while url:
        print('Request to {}'.format(url))

        browser.get(url)

        items = browser.find_elements_by_css_selector('.searchresultitem')

        item_count = 1
        for item in items:
            title_ele = item.find_element_by_css_selector(
                '.content.title > h2 > a')
            
            title = title_ele.get_attribute('title')
            item_url = title_ele.get_attribute('href')

            price = item.find_element_by_css_selector(
                '.content.description.price .important').text
            price = int(re.sub(r'[円,]', '', price))

            shipping_eles = item.find_elements_by_css_selector(
                '.content.description.price .-shipping')

            shipping = None
            if len(shipping_eles):
                for shipping_ele in shipping_eles:
                    shipping_str = shipping_ele.text
                    if re.match(r'送料無料.*', shipping_str):
                        shipping = 0
            else:
                shipping_eles = item.find_elements_by_css_selector(
                    '.description.shipping.with-help')
                if len(shipping_eles):
                    for shipping_ele in shipping_eles:
                        shipping_str = shipping_ele.text
                        m = re.search(r'\d+', shipping_str)
                        shipping = int(m.group())

            point_eles = item.find_elements_by_css_selector('.content.points')

            point = None
            if len(point_eles):
                for point_ele in point_eles:
                    point_str = point_ele.text
                    m = re.match(r'\d+', point_str)
                    point = int(m.group())

            review_scores_eles = item.find_elements_by_css_selector(
                '.content.review > a > span.score')

            review_score = None
            if len(review_scores_eles):
                for review_score_ele in review_scores_eles:
                    review_score = float(review_score_ele.text)

            review_nums_eles = item.find_elements_by_css_selector(
                '.content.review > a > span.legend')

            review_nums = None
            if len(review_nums_eles):
                for review_nums_ele in review_nums_eles:
                    m = re.search(r'\d+', review_nums_ele.text)
                    review_nums = int(m.group())

            results.append(
                (title, price, shipping, point, review_score, review_nums, item_url))
            item_count += 1

        try:
            url = browser.find_element_by_css_selector(
                'a.item.-next.nextPage').get_attribute('href')
        except:
            url = None

    return results


def get_save_file_name(params: dict) -> str:
    # file_name = ''
    # for key, value in params.items():
    #     key_value = ''
    #     if file_name:
    #         key_value = '_{}+{}'.format(key, value)
    #     else:
    #         key_value = 'data_{}+{}'.format(key, value)
    #     file_name += key_value
    # file_name += '.csv'
    return 'data.csv' 


def save_to_csv(file_name: str, data: List):
    with open(os.path.join(os.getcwd(), file_name), 'w') as f:
        writer = csv.writer(f)
        writer.writerow(('title', 'price', 'shipping', 'point',
                         'review_score', 'review_nums', 'item_url'))
        writer.writerows(data)


if __name__ == '__main__':
    main(sys.argv)