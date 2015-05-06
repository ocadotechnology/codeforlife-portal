import urllib3
import json

http = urllib3.PoolManager()

def is_GB(component):
    return 'country' in component['types'] and component['short_name'] == 'GB'

def extract_locality(components):
    for component in components:
        if 'locality' in component['types']:
            return component['long_name']

        if 'postal_town' in component['types']:
            return component['long_name']
    
    return None

def extract_location_data(results):
    for result in results:
        for component in result['address_components']:
            locality = extract_locality(result['address_components'])
            location = result['geometry']['location']
            return locality, location['lat'], location['lng']

    return None, None, None

def extract_country(results):
    for result in results:
        for component in result['address_components']:
            if 'country' in component['types']:
                return component['short_name']
    return 'UK'

# Uses Google Maps API to lookup location data using postcode + country(ISO 3166-1 alpha-2)
# By using country, it can return a more accurate location as the same postcode may exist in multiple countries
# Coordinates of the country will be returned if postcode is invalid in that country
# Return format is:
#     error, town, latitude, longitude
# If error is None then all went well,
# else error is not None and town, lat, lng = '0'
def lookup_coord(postcode, country):

    res = http.request('GET', 'http://maps.googleapis.com/maps/api/geocode/json',
                      fields={'address': postcode, 'components': 'country:' + country})

    data = json.loads(res.data)
    status = data.get('status', 'No status')
    results = data.get('results', [])

    if not res.status == 200:
        return 'Request error: %s' % status, '0', '0', '0'

    if not (status == 'OK' and len(results) > 0):
        return 'API error: %s' % , '0', '0', '0'

    town, lat, lng = extract_location_data(results)

    if town is None:
        return 'No town', '0', lat, lng

    return None, town, lat, lng

# Using the Google Map API, lookup country using postcode
# Returns error (if any) and country code (ISO 3166-1 alpha-2)
def lookup_country(postcode):
    default = 'UK'
    res = http.request('GET', 'http://maps.googleapis.com/maps/api/geocode/json',
                       fields={'address': postcode})
    data = json.loads(res.data)
    status = data.get('status', 'No status')
    results = data.get('results', [])

    if not res.status == 200:
        return 'Request error: %s' % res.status, default

    if not (status == 'OK' and len(results) > 0):
        return 'API error: %s' % status, default

    country = extract_country(results)

    if country is None:
        return 'Cannot determine country', default

    return None, country