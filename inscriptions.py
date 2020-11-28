import requests
import xml.etree.ElementTree as etree
import datetime

FUNCTION_GET_EVENTS = 'calevents_list'
FUNCTION_GET_DETAILED_EVENT = 'calevents_details'
FUNCTION_GET_ALL_CHARACTERS = 'points'


def build_request(base, function, api_token, *opts):
    request = base + '?function=' + function
    for opt in opts:
        request += '&' + opt['key'] + '=' + opt['value']

    request += '&atoken=' + api_token + '&atype=api'
    return request


def get_next_raids(api_url_base, api_token):
    api_url = build_request(api_url_base, FUNCTION_GET_EVENTS, api_token, {'key': 'raids_only', 'value': '1'})
    response = requests.get(api_url)

    if response.status_code == 200:
        next_raids = []
        raids = etree.fromstring(response.content.decode('utf-8').replace('\n', ''))
        for raid in raids.find('events'):
            raid_start_timestamp = int(raid.find('start_timestamp').text)
            if (datetime.datetime.fromtimestamp(raid_start_timestamp)) > datetime.datetime.now():
                next_raids.append(raid)
        if len(next_raids) > 0:
            return next_raids

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
        inactive_mains = []
        for char in all_chars.find('players'):
            char_id = int(char.find('id').text)
            main_name = char.find('main_name').text
            main_id = int(char.find('main_id').text)
            if char.find('active').text == '1':
                if main_name not in main_active_chars:
                    main_active_chars[main_name] = []
                main_active_chars[main_name].append(char_id)
            elif char_id == main_id:
                inactive_mains.append(main_name)

        # Ugly trick to remove entries for inactive mains as rerolls can be active for an inactive main
        for inactive_main in inactive_mains:
            main_active_chars.pop(inactive_main, None)

        return main_active_chars

    return None


def get_not_signed_in_users(detailed_raid, main_active_chars):
    not_signed_in = dict(main_active_chars)
    for user in detailed_raid.find('raidstatus').iter('char'):
        user_id = int(user.find('id').text)
        for main_active_char_key in main_active_chars.keys():
            if user_id in main_active_chars[main_active_char_key]:
                not_signed_in.pop(main_active_char_key, None)
                break

    return not_signed_in.keys()


def check_next_raid_inscriptions(api_url_base, api_token, force_next, days_check_min=1, days_check_max=2, date=None):
    next_raids = get_next_raids(api_url_base, api_token)
    if next_raids is not None:
        for next_raid in next_raids:
            next_raid_start_timestamp = int(next_raid.find('start_timestamp').text)
            next_raid_start_datetime = datetime.datetime.fromtimestamp(next_raid_start_timestamp)

            # If a date is provided: find if a raid is at the same date as the given one
            # If not check if we want to find the next raid, whatever the date is
            # Else, check if the raid is in the given time period
            if next_raid_start_datetime.date() == date \
                    or (date is None and (force_next or
                                          (next_raid_start_datetime - datetime.timedelta(
                                              days=int(days_check_min))) < datetime.datetime.now()
                                          < (next_raid_start_datetime - datetime.timedelta(days=int(days_check_max))))):
                next_raid_id = next_raid.find('eventid').text
                det_raid = get_raid_detailed_info(next_raid_id, api_url_base, api_token)
                main_active_chars = get_main_active_chars(api_url_base, api_token)
                return {'date': next_raid_start_datetime.strftime('%d/%m/%Y'),
                        'raid_id': next_raid_id,
                        'not_checked_in_users': get_not_signed_in_users(det_raid, main_active_chars)}

    return None
