from http import HTTPStatus
from api.api_client import ApiClient\

import pytest

from assertions.objects_assertion import *
from api.objects_api import *
from assertions.assertion_base import *

from models.object_models import *
from utilities.files_utils import read_json_test_data, read_json_common_request_data


class TestObjects:
    """ Тесты /objects """

    @pytest.fixture(scope='class')
    def client(self):
        return ApiClient()

    def test_get_objects(self, client, request):
        """
        получение заранее заготовленных объектов из базы с параметрами по-умолчанию,
        GET /objects
        """
        # получаем объекты из базы
        response = get_objects(client)

        # убеждаемся, что в ответ пришли объекты, которые мы ожидаем
        assert_status_code(response, HTTPStatus.OK)
        assert_response_body_fields(request, response)











