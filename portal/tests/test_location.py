# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
import json
import os
import unittest

import requests
import responses

from portal.helpers.location import lookup_coord, lookup_country

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Returns a string read from the given file that can be deserialised into json objects
def read_json_from_file(filename):
    data = ""

    if filename:
        f = open(filename, "r")
        data = f.read()
        f.close()

    return data


# Returns path to the file that contains the json response
def datafile(filename):
    return os.path.join(DATA_DIR, filename)


MAPS_API_GEOCODE_JSON = "https://maps.googleapis.com/maps/api/geocode/json?"


class TestLocation(unittest.TestCase):
    def assert_default_coord(self, town, lat, lng):
        # default values returned when error occurs in lookup_coord()
        self.assertEqual((town, lat, lng), (0, 0, 0))

    def assert_default_country_and_coord(self, country, town, lat, lng):
        # default values returned when error occurs in lookup_country()
        self.assertEqual((country, town, lat, lng), ("GB", 0, 55.378051, -3.435973))

    @responses.activate
    def test_lookup_coord_call_api_once(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=SW72AZ&components=country:GB",
            body=read_json_from_file(datafile("sw72az_gb.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_coord("SW72AZ", "GB")
        self.assertEqual(len(responses.calls), 1, "API was called more than once")

    @responses.activate
    def test_lookup_coord_json_unchanged(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=SW72AZ&components=country:GB",
            body=read_json_from_file(datafile("sw72az_gb.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_coord("SW72AZ", "GB")
        self.assertEqual(
            responses.calls[0].response.json(),
            json.loads(read_json_from_file(datafile("sw72az_gb.json"))),
        )

    @responses.activate
    def test_lookup_coord_valid_postcode_country_gb1(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=SW72AZ&components=country:GB",
            body=read_json_from_file(datafile("sw72az_gb.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_coord("SW72AZ", "GB")
        self.assertEqual(result, (None, "GB", "London", 51.5005046, -0.1782187))

    @responses.activate
    def test_lookup_coord_valid_postcode_country_gb2(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=AL10 9NE&components=country:GB",
            body=read_json_from_file(datafile("al109ne_gb.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_coord("AL10 9NE", "GB")
        self.assertEqual(result, (None, "GB", "Hatfield", 51.7623259, -0.2438929))

    # Default to coordinates of country
    @responses.activate
    def test_lookup_coord_invalid_postcode_country_gb(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=10000&components=country:GB",
            body=read_json_from_file(datafile("10000_gb.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_coord("10000", "GB")
        self.assertEqual(result, (None, "GB", 0, 55.378051, -3.435973))

    @responses.activate
    def test_lookup_coord_invalid_postcode_country_kr(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=AL109NE&components=country:KR",
            body=read_json_from_file(datafile("al109ne_kr.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_coord("AL109NE", "KR")
        self.assertEqual(result, (None, "KR", 0, 35.907757, 127.766922))

    @responses.activate
    def test_lookup_coord_connection_error(self):
        error, country, town, lat, lng = lookup_coord("AL109NE", "GB")
        assert "Connection error" in error
        self.assert_default_coord(town, lat, lng)

    @responses.activate
    def test_lookup_coord_cannot_decode_json(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=AL109NE&components=country:GB",
            body="",
            match_querystring=True,
            content_type="application/json",
        )
        error, country, town, lat, lng = lookup_coord("AL109NE", "GB")
        assert "Value error" in error
        self.assert_default_coord(town, lat, lng)

    @responses.activate
    def test_lookup_coord_request_error_404(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=AL109NE&components=country:GB",
            body=read_json_from_file(datafile("al109ne_gb.json")),
            status=requests.codes.not_found,
            match_querystring=True,
            content_type="application/json",
        )
        error, country, town, lat, lng = lookup_coord("AL109NE", "GB")
        assert "Request error" in error
        self.assert_default_coord(town, lat, lng)

    @responses.activate
    def test_lookup_coord_zero_results(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "address=AL109NE&components=country:AB",
            body=read_json_from_file(datafile("al109ne_ab.json")),
            match_querystring=True,
            content_type="application/json",
        )
        error, country, town, lat, lng = lookup_coord("AL109NE", "AB")
        assert "API error" in error
        self.assert_default_coord(town, lat, lng)

    @responses.activate
    def test_lookup_country_valid_postcode1(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "components=postal_code:SW72AZ",
            body=read_json_from_file(datafile("sw72az.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_country("SW72AZ")
        self.assertEqual(result, (None, "GB", "London", 51.5005046, -0.1782187))

    @responses.activate
    def test_lookup_country_valid_postcode1(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "components=postal_code:AL10 9NE",
            body=read_json_from_file(datafile("al109ne.json")),
            match_querystring=True,
            content_type="application/json",
        )
        result = lookup_country("AL10 9NE")
        self.assertEqual(result, (None, "GB", "Hatfield", 51.7623259, -0.2438929))

    @responses.activate
    def test_lookup_country_invalid_postcode_zero_results(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "components=postal_code:xxxxx",
            body=read_json_from_file(datafile("xxxxx.json")),
            match_querystring=True,
            content_type="application/json",
        )
        error, country, town, lat, lng = lookup_country("xxxxx")
        assert "API error" in error
        self.assert_default_country_and_coord(country, town, lat, lng)

    @responses.activate
    def test_lookup_country_connection_error(self):
        error, country, town, lat, lng = lookup_country("xxxxx")
        assert "Connection error" in error

    @responses.activate
    def test_lookup_country_request_error_404(self):
        responses.add(
            responses.GET,
            MAPS_API_GEOCODE_JSON + "components=postal_code:AL109NE",
            body=read_json_from_file(datafile("al109ne.json")),
            status=requests.codes.not_found,
            match_querystring=True,
            content_type="application/json",
        )
        error, country, town, lat, lng = lookup_country("AL109NE")
        assert "Request error" in error
        self.assert_default_country_and_coord(country, town, lat, lng)
