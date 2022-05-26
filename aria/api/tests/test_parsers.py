from django.http import HttpRequest

import orjson

from aria.api.parsers import CamelCaseParser, ORJSONParser


class TestAPIParsers:
    def test_orjson_parser(self):
        """
        Test that data is parsed as expected with orjson.
        """

        parser = ORJSONParser()
        data = {"first_name": "Test", "last_name": "User"}

        request = HttpRequest()

        # The orjson parser should only parse data as orjson instead
        # of json, so nothing in the payload should be mutated.
        request._body = orjson.dumps(data)
        parsed_data = parser.parse_body(request)

        # Assert that nothing changed from payload to parsed data.
        assert parsed_data == data

    def test_camel_case_parser(self):
        """
        Test that the parser parses data sent in as camelCase gets
        parsed as a python dict, and data sent in as snake_case only
        gets loaded from json to python dict.
        """

        parser = CamelCaseParser()
        data = {"first_name": "Test", "last_name": "User"}
        camelized_data = {"firstName": "Test", "lastName": "User"}

        request = HttpRequest()

        # Test that data sent in as snake_case remains snake_case.
        request._body = orjson.dumps(data)
        parsed_data = parser.parse_body(request)
        # Assert that nothing changed from payload to parsed data.
        assert parsed_data == data

        # Test that camelized data gets parsed as python dict.
        request._body = orjson.dumps(camelized_data)
        parsed_camel_case_data = parser.parse_body(request)
        # Assert that data has been converted, matching it to the
        # snake_cased data.
        assert parsed_camel_case_data == data
