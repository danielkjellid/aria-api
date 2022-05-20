from rest_framework import serializers
from rest_framework.schemas.openapi import AutoSchema


class APIViewSchema(AutoSchema):
    def get_component_name(self, serializer):
        """
        Override component name, assumes that it follows the
        pattern <model><viewmethod>API, e.g. UserListAPI.
        """

        # Use the qualname from the serializer class as component name
        # Returns Parent.SerializerName.
        component_name = serializer.__class__.__qualname__
        # Remove everythin from API and beyond.
        component_name = component_name.split("API", 1)[0]

        if component_name == "":
            raise Exception(
                '"{}" is an invalid class name for schema generation. '
                "View class's name should be unique and explicit.".format(
                    serializer.__class__.__qualname__
                )
            )

        return component_name

    def get_operation_id_base(self, path, method, action):
        return self.get_component_name(self.get_serializer(path, method))

    def get_serializer(self, path, method):
        method_func = getattr(self.view, method.lower())
        if hasattr(method_func, "_schema_serializer"):
            return method_func._schema_serializer
        return super().get_serializer(path, method)

    def get_filter_parameters(self, path, method):
        parameters = super().get_filter_parameters(path, method)
        method_func = getattr(self.view, method.lower())
        if hasattr(method_func, "_schema_query_parameters"):
            parameters += self.map_parameters_serializer(
                method_func._schema_query_parameters, "query"
            )
        return parameters

    def map_parameters_serializer(self, serializer, location):
        map_ = self.map_serializer(serializer)
        parameters = []
        for name in map_["properties"]:
            parameter = {
                "name": name,
                "in": location,
            }
            if "required" in map_ and name in map_["required"]:
                parameter["required"] = True
            if "description" in map_["properties"][name]:
                parameter["description"] = map_["properties"][name]["description"]
            parameter["schema"] = {
                k: v for k, v in map_["properties"][name].items() if k != "description"
            }
            parameters.append(parameter)
        return parameters

    @staticmethod
    def serializer(serializer: serializers.Serializer):
        def aux(func):
            func._schema_serializer = serializer
            return func

        return aux

    @staticmethod
    def query_parameters(parameters: serializers.Serializer):
        def aux(func):
            func._schema_query_parameters = parameters
            return func

        return aux
