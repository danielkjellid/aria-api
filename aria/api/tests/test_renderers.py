import orjson

from aria.api.renderers import CamelCaseRenderer


class TestAPIRenderers:
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
