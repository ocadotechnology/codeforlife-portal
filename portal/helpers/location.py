import urllib3
import json

http = urllib3.PoolManager()

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
        return town, location['lat'], location['lng'], country

    return None, None, None, None

# Uses Google Maps API to lookup location data using postcode + country(ISO 3166-1 alpha-2)
# By using country, it can return a more accurate location as the same postcode may exist in multiple countries
# Coordinates of the country will be returned if postcode is invalid in that country
# Return format is:
#     error, town, latitude, longitude
# If error is None then all went well,
# else error is not None and town, lat, lng = '0'
def lookup_coord(postcode, country):

    # Catch error when there is a problem connecting to external API
    try:
        res = http.request('GET', 'http://maps.googleapis.com/maps/api/geocode/json',
                            fields={'address': postcode, 'components': 'country:' + country})
    except urllib3.exceptions.HTTPError:
        return 'Http error', '0', '0', '0'

    data = json.loads(res.data)
    status = data.get('status', 'No status')
    results = data.get('results', [])

    if not res.status == 200:
        return 'Request error: %s' % res.status, '0', '0', '0'

    #
    if not (status == 'OK' and len(results) > 0):
        return 'API error: %s' % status, '0', '0', '0'

    town, lat, lng, country = extract_location_data(results)

    if town is None:
        return 'No town', '0', lat, lng

    return None, town, lat, lng

# Using the Google Map API, lookup country using postcode
# Returns error (if any) and country code (ISO 3166-1 alpha-2)
def lookup_country(postcode):
    # default location is UK and the coordinates of UK
    default_country = 'GB'
    default_town = '0'
    default_lat = '55.378051'
    default_lng = '-3.435973'

    # Catch error when there is a problem connecting to external API
    try:
        res = http.request('GET', 'http://maps.googleapis.com/maps/api/geocode/json',
                            fields={'components': 'postal_code:' + postcode})
    except urllib3.exceptions.HTTPError:
        return 'Http Error', default_country, default_town, default_lat, default_lng

    data = json.loads(res.data)
    status = data.get('status', 'No status')
    results = data.get('results', [])

    if not res.status == 200:
        return 'Request error: %s' % res.status, default_country, default_town, default_lat, default_lng

    if not (status == 'OK' and len(results) > 0):
        return 'API error: %s' % status, default_country, default_town, default_lat, default_lng

    town, lat, lng, country = extract_location_data(results)

    if country is None:
        return 'Cannot determine country', default_country, default_town, default_lat, default_lng

    return None, country, town, lat, lng