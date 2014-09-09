import requests
import json

def is_GB(component):
    return 'country' in component['types'] and component['short_name'] == 'GB'

def extract_locality(components, school):
    for component in components:
        if 'locality' in component['types']:
            school.town = component['long_name']
            return True

    return False

def extract_location_data(results, school):
    for result in results:
        for component in result['address_components']:
            if is_GB(component) and extract_locality(result['address_components'], school):
                location = result['geometry']['location']
                school.latitude = location['lat']
                school.longitude = location['lng']
                return True

    return False

def fill_in_location(school):
    res = requests.get('https://maps.googleapis.com/maps/api/geocode/json', params={
        'address': school.postcode,
    })

    data = res.json()
    return res.status_code == requests.codes.ok and \
           data.get('status', '') == 'OK' and \
           len(data.get('results', [])) > 0 and \
           extract_location_data(data['results'], school)