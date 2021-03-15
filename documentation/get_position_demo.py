#!/usr/bin/env python3
import requests
def get_position_from_spi(date_str):
    auth = (user, password)
    params = {'date': date_str}
    r = requests.get('https://scdm-ace.swisspolar.ch/api/position', params=params, auth=auth)
    result = r.json()
    return result['latitude'], result['longitude']
position = get_position_from_spi('2017-01-28T21:00:00+00:00')
print(position)
