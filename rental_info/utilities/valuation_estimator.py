import requests


# https://blog.quandl.com/api-for-housing-data
base_url = 'https://www.quandl.com/api/v3/datasets/ZILL/'
param_dict = {'api_key': '8Uyu2uqj7S1Zt6x_SHA_'}
json_format = 'json'
csv_format = 'csv'
INDICATORS = {'rent_per_square_foot': 'RZSF', 'estimated_rent': 'RAH',
              'median_rent': 'RMP', 'price_to_rent': 'PRR',
              'median_list_price_per_square_foot': 'MLPSF'}


def get_price_series(zipcode, indicator):
    # url = "https://www.quandl.com/api/v3/datasets/ZILL/Z94404_RZSF.json?api_key=8Uyu2uqj7S1Zt6x_SHA_"
    url_endpoint = '%sZ%s_%s.%s' % (base_url, zipcode.strip(), indicator, json_format)
    response = requests.get(url_endpoint, params=param_dict)
    return response.json()


def get_metadata(zipcode, indicator):
    # url = "https://www.quandl.com/api/v3/datasets/ZILL/Z94404_RZSF/metadata.json?api_key=8Uyu2uqj7S1Zt6x_SHA_"
    url_endpoint = '%sZ%s_%s/%s.%s' % (base_url, zipcode, indicator, 'metadata', json_format)
    response = requests.get(url_endpoint, params=param_dict)
    return response.json()


def get_latest_price(zipcode, indicator):
    response_json = get_price_series(zipcode.strip(), indicator)
    latest_date = response_json['dataset']['newest_available_date']
    for d in response_json['dataset']['data']:
        if d[0] == latest_date:
            return d[1], latest_date
    # shouldn't happen but if it happens there's been an error
    return -1, latest_date


# print get_price_series(94404, INDICATORS['estimated_rent'])
# print get_metadata(94404, INDICATORS['estimated_rent'])
# print get_latest_price(94404, INDICATORS['rent_per_square_foot'])
