import datetime
import mimetypes
import os
import re
import tempfile

from lumapps.latest.api.exceptions import ApiException


class SerializationError(ApiException):
    pass


class Serialization(object):

    PRIMITIVE_TYPES = (float, bool, bytes, str, int)
    NATIVE_TYPES_MAPPING = {
        "int": int,
        "long": int,
        "float": float,
        "str": str,
        "bool": bool,
        "date": datetime.date,
        "datetime": datetime.datetime,
        "object": object,
    }

    def __init__(self, models) -> None:
        self.models = models

    def sanitize_for_serialization(self, obj):
        """Builds a JSON POST object.

        If obj is None, return None.
        If obj is str, int, long, float, bool, return directly.
        If obj is datetime.datetime, datetime.date
            convert to string in iso8601 format.
        If obj is list, sanitize each element in the list.
        If obj is dict, return the dict.
        If obj is swagger model, return the properties dict.

        :param obj: The data to serialize.
        :return: The serialized form of data.
        """
        if obj is None:
            return None
        elif isinstance(obj, self.PRIMITIVE_TYPES):
            return obj
        elif isinstance(obj, list):
            return [self.sanitize_for_serialization(sub_obj) for sub_obj in obj]
        elif isinstance(obj, tuple):
            return tuple(self.sanitize_for_serialization(sub_obj) for sub_obj in obj)
        elif isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()

        if isinstance(obj, dict):
            obj_dict = obj
        else:
            # Convert model obj to dict except
            # attributes `swagger_types`, `attribute_map`
            # and attributes which value is not None.
            # Convert attribute name to json key in
            # model definition for request.
            obj_dict = {
                obj.attribute_map[attr]: getattr(obj, attr)
                for attr, _ in obj.swagger_types.items()
                if getattr(obj, attr) is not None
            }

        return {
            key: self.sanitize_for_serialization(val) for key, val in obj_dict.items()
        }

    def deserialize(self, data: dict, klass):
        """Deserializes dict, list, str into an object.

        :param data: dict, list or str.
        :param klass: class literal, or string of class name.

        :return: object.
        """
        if data is None:
            return None

        if type(klass) == str:
            if klass.startswith("list["):
                sub_kls = re.match(r"list\[(.*)\]", klass).group(1)
                return [self.deserialize(sub_data, sub_kls) for sub_data in data]

            if klass.startswith("dict("):
                sub_kls = re.match(r"dict\(([^,]*), (.*)\)", klass).group(2)
                return {k: self.deserialize(v, sub_kls) for k, v in data.items()}

            # convert str to class
            if klass in self.NATIVE_TYPES_MAPPING:
                klass = self.NATIVE_TYPES_MAPPING[klass]
            else:
                klass = getattr(self.models, klass)

        if klass in self.PRIMITIVE_TYPES:
            return self.__deserialize_primitive(data, klass)
        elif klass == object:
            return self.__deserialize_object(data)
        elif klass == datetime.date:
            return self.__deserialize_date(data)
        elif klass == datetime.datetime:
            return self.__deserialize_datatime(data)
        else:
            return self.__deserialize_model(data, klass)

    def parameters_to_tuples(self, params, collection_formats):
        """Get parameters as list of tuples, formatting collections.

        :param params: Parameters as dict or list of two-tuples
        :param dict collection_formats: Parameter collection formats
        :return: Parameters as list of tuples, collections formatted
        """
        new_params = []
        if collection_formats is None:
            collection_formats = {}
        for k, v in (
            params.items() if isinstance(params, dict) else params
        ):  # noqa: E501
            if k in collection_formats:
                collection_format = collection_formats[k]
                if collection_format == "multi":
                    new_params.extend((k, value) for value in v)
                else:
                    if collection_format == "ssv":
                        delimiter = " "
                    elif collection_format == "tsv":
                        delimiter = "\t"
                    elif collection_format == "pipes":
                        delimiter = "|"
                    else:  # csv is the default
                        delimiter = ","
                    new_params.append((k, delimiter.join(str(value) for value in v)))
            else:
                new_params.append((k, v))
        return new_params

    def prepare_post_parameters(self, post_params=None, files=None):
        """Builds form parameters.

        :param post_params: Normal form parameters.
        :param files: File parameters.
        :return: Form parameters with files.
        """
        params = []

        if post_params:
            params = post_params

        if files:
            for k, v in files.items():
                if not v:
                    continue
                file_names = v if type(v) is list else [v]
                for n in file_names:
                    with open(n, "rb") as f:
                        filename = os.path.basename(f.name)
                        filedata = f.read()
                        mimetype = (
                            mimetypes.guess_type(filename)[0]
                            or "application/octet-stream"
                        )
                        params.append(tuple([k, tuple([filename, filedata, mimetype])]))

        return params

    def select_header_accept(self, accepts):
        """Returns `Accept` based on an array of accepts provided.

        :param accepts: List of headers.
        :return: Accept (e.g. application/json).
        """
        if not accepts:
            return

        accepts = [x.lower() for x in accepts]

        if "application/json" in accepts:
            return "application/json"
        else:
            return ", ".join(accepts)

    def select_header_content_type(self, content_types):
        """Returns `Content-Type` based on an array of content_types provided.

        :param content_types: List of content-types.
        :return: Content-Type (e.g. application/json).
        """
        if not content_types:
            return "application/json"

        content_types = [x.lower() for x in content_types]

        if "application/json" in content_types or "*/*" in content_types:
            return "application/json"
        else:
            return content_types[0]

    def update_params_for_auth(self, headers, querys, auth_settings):
        """Updates header and query params based on authentication setting.

        :param headers: Header parameters dict to be updated.
        :param querys: Query parameters tuple list to be updated.
        :param auth_settings: Authentication setting identifiers list.
        """
        if not auth_settings:
            return

        for auth in auth_settings:
            auth_setting = self.configuration.auth_settings().get(auth)
            if auth_setting:
                if not auth_setting["value"]:
                    continue
                elif auth_setting["in"] == "header":
                    headers[auth_setting["key"]] = auth_setting["value"]
                elif auth_setting["in"] == "query":
                    querys.append((auth_setting["key"], auth_setting["value"]))
                else:
                    raise ValueError(
                        "Authentication token must be in `query` or `header`"
                    )

    def __deserialize_file(self, response):
        """Deserializes body to file

        Saves response body into a file in a temporary folder,
        using the filename from the `Content-Disposition` header if provided.

        :param response:  RESTResponse.
        :return: file path.
        """
        fd, path = tempfile.mkstemp(dir=self.configuration.temp_folder_path)
        os.close(fd)
        os.remove(path)

        content_disposition = response.getheader("Content-Disposition")
        if content_disposition:
            filename = re.search(
                r'filename=[\'"]?([^\'"\s]+)[\'"]?', content_disposition
            ).group(1)
            path = os.path.join(os.path.dirname(path), filename)
            response_data = response.data
            with open(path, "wb") as f:
                if isinstance(response_data, str):
                    # change str to bytes so we can write it
                    response_data = response_data.encode("utf-8")
                    f.write(response_data)
                else:
                    f.write(response_data)
        return path

    def __deserialize_primitive(self, data, klass):
        """Deserializes string to primitive type.

        :param data: str.
        :param klass: class literal.

        :return: int, long, float, str, bool.
        """
        try:
            return klass(data)
        except UnicodeEncodeError:
            return str
        except TypeError:
            return data

    def __deserialize_object(self, value):
        """Return a original value.

        :return: object.
        """
        return value

    def __deserialize_date(self, string):
        """Deserializes string to date.

        :param string: str.
        :return: date.
        """
        try:
            from dateutil.parser import parse

            return parse(string).date()
        except ImportError:
            return string
        except ValueError:
            raise SerializationError(f"Failed to parse `{string}` as date object")

    def __deserialize_datatime(self, string):
        """Deserializes string to datetime.

        The string should be in iso8601 datetime format.

        :param string: str.
        :return: datetime.
        """
        try:
            from dateutil.parser import parse

            return parse(string)
        except ImportError:
            return string
        except ValueError:
            raise SerializationError(f"Failed to parse `{string}` as datetime object")

    def __hasattr(self, object, name):
        return name in object.__class__.__dict__

    def __deserialize_model(self, data, klass):
        """Deserializes list or dict to model.

        :param data: dict, list.
        :param klass: class literal.
        :return: model object.
        """

        if not klass.swagger_types and not self.__hasattr(
            klass, "get_real_child_model"
        ):
            return data

        kwargs = {}
        if klass.swagger_types is not None:
            for attr, attr_type in klass.swagger_types.items():
                if (
                    data is not None
                    and klass.attribute_map[attr] in data
                    and isinstance(data, (list, dict))
                ):
                    value = data[klass.attribute_map[attr]]
                    kwargs[attr] = self.deserialize(value, attr_type)

        instance = klass(**kwargs)

        if (
            isinstance(instance, dict)
            and klass.swagger_types is not None
            and isinstance(data, dict)
        ):
            for key, value in data.items():
                if key not in klass.swagger_types:
                    instance[key] = value
        if self.__hasattr(instance, "get_real_child_model"):
            klass_name = instance.get_real_child_model(data)
            if klass_name:
                instance = self.deserialize(data, klass_name)
        return instance


"""
Serialization usage

        # header parameters
        header_params = self.sanitize_for_serialization(header_params)
        header_params = dict(self.parameters_to_tuples(header_params,
                                                       collection_formats))

        # path parameters
        path_params = self.sanitize_for_serialization(path_params)
        path_params = self.parameters_to_tuples(path_params,
                                                collection_formats)
        for k, v in path_params:
            # specified safe chars, encode everything
            resource_path = resource_path.replace(
                '{%s}' % k,
                quote(str(v), safe=config.safe_chars_for_path_param)
            )

        # query parameters
        query_params = self.sanitize_for_serialization(query_params)
        query_params = self.parameters_to_tuples(query_params,
                                                 collection_formats)

        # post parameters
        post_params = self.prepare_post_parameters(post_params, files)
        post_params = self.sanitize_for_serialization(post_params)
        post_params = self.parameters_to_tuples(post_params,
                                                collection_formats)
"""
