import requests
import exceptions

def is_GB(component):
    return 'country' in component['types'] and component['short_name'] == 'GB'

def extract_locality(components):
    town = None
    country = None

    for component in components:
        if 'locality' in component['types']:
            town = component['long_name']

        if 'postal_town' in component['types']:
            town = component['long_name']

        if 'country' in component['types']:
            country = component['short_name']
    
    return town, country

def extract_location_data(results):
    for result in results:
        town, country = extract_locality(result['address_components'])
        location = result['geometry']['location']
        return country, town, location['lat'], location['lng']

    return None, None, None, None

# Uses Google Maps API to lookup location data using postcode + country(ISO 3166-1 alpha-2)
# By using country, it can return a more accurate location as the same postcode may exist in multiple countries
# Coordinates of the country will be returned if postcode is invalid in that country
# Return format is:
#     error, town, latitude, longitude
# If error is None then all went well,
# else error is not None and town, lat, lng = '0'
def lookup_coord(postcode, country):

    payload = {'address': postcode, 'components': 'country:' + country}

    return get_location_from_api(payload)

# Using the Google Map API, lookup country using postcode
# Returns error (if any) and country code (ISO 3166-1 alpha-2)
def lookup_country(postcode):

    payload = {'components': 'postal_code:' + postcode}

    return get_location_from_api(payload)

def get_location_from_api(payload):
    # default location is UK and the coordinates of UK
    default_country = 'GB'
    default_town = 0
    default_lat = 55.378051
    default_lng = -3.435973

    if 'country' in payload.get('components'):
        default_country = payload.get('components', 'GB').rpartition(':')[2]
        default_town = default_lat = default_lng = 0

    # Catch error when there is a problem connecting to external API
    try:
        res = requests.get('https://maps.googleapis.com/maps/api/geocode/json',
                           params=payload)
    except requests.exceptions.RequestException:
        return 'Connection error', default_country, default_town, default_lat, default_lng

    # Make sure status_code is 200 before deserialising json
    if not res.status_code == requests.codes.ok:
        return 'Request error: %s' % res.reason, default_country, default_town, default_lat, default_lng

    try:
        data = res.json()
    except exceptions.ValueError as e:
        return 'Value error: %s' % e, default_country, default_town, default_lat, default_lng

    status = data.get('status', 'No status')
    results = data.get('results', [])

    if not (status == 'OK' and len(results) > 0):
        return 'API error: %s' % status, default_country, default_town, default_lat, default_lng

    country, town, lat, lng = extract_location_data(results)

    return None, country or default_country, town or default_town, lat or default_lat, lng or default_lng
