import orjson

from aria.api.renderers import CamelCaseRenderer, ORJSONRenderer


class TestAPIRenderers:
    def test_orjson_renderer(self) -> None:
        renderer = ORJSONRenderer()
        data = {"first_name": "Test", "last_name": "User", "is_active": True}

        rendered_data = renderer.render(None, data, response_status=200)

        actual_output = orjson.loads(rendered_data)
        # We don't expect orjson to change anything about the returned response, so it should
        # be the same as the data once loaded.
        expected_output = {"first_name": "Test", "last_name": "User", "is_active": True}

        assert actual_output == expected_output

    def test_camel_case_renderer(self) -> None:
        """
        Test that the camel case renderer renders content camel case.
        """

        renderer = CamelCaseRenderer()
        data = {"first_name": "Test", "last_name": "User", "is_active": True}

        rendered_data = renderer.render(None, data, response_status=200)

        actual_output = orjson.loads(rendered_data)
        # Expect that keys are camelCase.
        expected_output = {"firstName": "Test", "lastName": "User", "isActive": True}

        assert actual_output == expected_output
