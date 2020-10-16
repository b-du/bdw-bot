import requests
import xml.etree.ElementTree as etree
import datetime

FUNCTION_GET_EVENTS = 'calevents_list'
FUNCTION_GET_DETAILED_EVENT= 'calevents_details'
FUNCTION_GET_ALL_CHARACTERS = 'points'


def build_request(base, function, api_token, *opts):
    request = base + '?function=' + function
    for opt in opts:
        request += '&' + opt['key'] + '=' + opt['value']

    request += '&atoken=' + api_token + '&atype=api'
    return request


def get_next_raid(api_url_base, api_token):
    api_url = build_request(api_url_base, FUNCTION_GET_EVENTS, api_token, {'key': 'raids_only', 'value': '1'}, {'key': 'number', 'value': '3'})
    response = requests.get(api_url)

    if response.status_code == 200:
        raids = etree.fromstring(response.content.decode('utf-8').replace('\n', ''))
        for raid in raids.find('events'):
            raid_start_timestamp = int(raid.find('start_timestamp').text)
            if (datetime.datetime.fromtimestamp(raid_start_timestamp)) > datetime.datetime.now():
                return raid

    return None


def get_raid_detailed_info(raid_id, api_url_base, api_token):
    api_url = build_request(api_url_base, FUNCTION_GET_DETAILED_EVENT, api_token, {'key': 'eventid', 'value': raid_id})
    response = requests.get(api_url)

    if response.status_code == 200:
        detailed_raid = etree.fromstring(response.content.decode('utf-8').replace('\n', ''))
        return detailed_raid

    return None


def get_main_active_chars(api_url_base, api_token):
    api_url = build_request(api_url_base, FUNCTION_GET_ALL_CHARACTERS, api_token)
    response = requests.get(api_url)

    if response.status_code == 200:
        main_active_chars = {}
        all_chars = etree.fromstring(response.content.decode('utf-8').replace('\n', ''))
        for char in all_chars.find('players'):
            id = char.find('id').text
            main_id = char.find('main_id').text
            if id == main_id and char.find('active').text == '1':
                main_active_chars[int(id)] = char.find('name').text

        return main_active_chars

    return None


def get_not_signed_in_users(detailed_raid, main_active_chars):
    not_signed_in = dict(main_active_chars)
    for user in detailed_raid.find('raidstatus').iter('char'):
        user_id = int(user.find('id').text)
        if not_signed_in.get(user_id, None) is not None:
            del not_signed_in[user_id]

    return not_signed_in.values()


def check_next_raid_inscriptions(time_before_next_raid, api_url_base, api_token):
    next_raid = get_next_raid(api_url_base, api_token)
    if next_raid is not None:
        next_raid_start_timestamp = int(next_raid.find('start_timestamp').text)

        # Is next raid in less than 2 days?
        if (datetime.datetime.fromtimestamp(next_raid_start_timestamp) - datetime.timedelta(days=time_before_next_raid)) < datetime.datetime.now():
            next_raid_id = next_raid.find('eventid').text
            det_raid = get_raid_detailed_info(next_raid_id, api_url_base, api_token)
            main_active_chars = get_main_active_chars(api_url_base, api_token)
            return get_not_signed_in_users(det_raid, main_active_chars)

    return None


at = 'ro79da0d2a0b72b0f0e7207ff97bf45a8e9a7d7990038850'
aub = 'http://bdw-amnnenar.fr/api.php'
check_next_raid_inscriptions(5, aub, at)
