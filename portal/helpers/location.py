import requests

try:
    from exceptions import Exception, ValueError
except ImportError:
    pass


class RequestException(Exception):
    pass


class ApiException(Exception):
    pass


def is_GB(component):
    return "country" in component["types"] and component["short_name"] == "GB"


def extract_locality(components):
    town = None
    country = None

    for component in components:
        if "locality" in component["types"]:
            town = component["long_name"]

        if "postal_town" in component["types"]:
            town = component["long_name"]

        if "country" in component["types"]:
            country = component["short_name"]

    return town, country


def extract_location_data(results):
    for result in results:
        town, country = extract_locality(result["address_components"])
        location = result["geometry"]["location"]
        return country, town, location["lat"], location["lng"]

    return None, None, None, None


# Uses Google Maps API to lookup location data using postcode + country(ISO 3166-1 alpha-2)
# By using country, it can return a more accurate location as the same postcode may exist in multiple countries
# Coordinates of the country will be returned if postcode is invalid in that country
def lookup_coord(postcode, country):

    payload = {"address": postcode, "components": "country:" + country}

    return get_location_from_api(payload)


# Using the Google Map API, lookup country using postcode
def lookup_country(postcode):

    payload = {"components": "postal_code:" + postcode}

    return get_location_from_api(payload)


# Takes in payload as argument and use it when calling API
# Catches any error and return an error message as first element in the tuple
# Coordinates of GB is used if country is not specified, otherwise default to original country and 0 for coordinates
# Return format is:
#     error, country, town, latitude, longitude
def get_location_from_api(payload):
    # default location is UK and the coordinates of UK
    default_country = "GB"
    default_town = 0
    default_lat = 55.378051
    default_lng = -3.435973

    if "country" in payload.get("components"):
        default_country = payload.get("components", "GB").rpartition(":")[2]
        default_town = default_lat = default_lng = 0

    # Catch error when there is a problem connecting to external API
    try:
        res = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json", params=payload
        )

        # Make sure status_code is 200 before deserialising json
        if not res.status_code == requests.codes.ok:
            raise RequestException(res.reason)

        data = res.json()

        status = data.get("status", "No status")
        results = data.get("results", [])

        if not (status == "OK" and len(results) > 0):
            raise ApiException(status)

        country, town, lat, lng = extract_location_data(results)

        return (
            None,
            country or default_country,
            town or default_town,
            lat or default_lat,
            lng or default_lng,
        )

    except requests.exceptions.RequestException:
        error = "Connection error"

    except RequestException as e:
        error = "Request error: %s" % e

    except ValueError as e:
        error = "Value error: %s" % e

    except ApiException as e:
        error = "API error: %s" % e

    return error, default_country, default_town, default_lat, default_lng
