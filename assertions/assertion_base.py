from typing import Type

from pydantic import BaseModel

from utilities.files_utils import read_json_file_data, read_json_common_response_data
from utilities.json_utils import compare_json_left_in_right, remove_ids


class LogMsg:
    """
    Базовый класс для построения логов AssertionError.
    Конструирует сообщение в свое поле _msg.
    """

    def __init__(self, where, response):
        self._msg = ''
        self._response = response
        self._where = where

    def add_request_url(self):
        """
        добавляет данные об отправленном на сервер запросе
        """
        self._msg += f"The content of the sent request (url, query params, body):\n" \
                     f"\tURL: {self._response.request.url}\n"
        self._msg += f"\tmethod: {self._response.request.method}\n"
        self._msg += f"\theaders: {dict(self._response.request.headers)}\n"
        if hasattr(self._response.request, 'params') and self._response.request.params:
            self._msg += f"\tquery params: {self._response.request.params}\n"
        else:
            self._msg += f"\tquery params:\n"
        if hasattr(self._response.request, 'content') and self._response.request.read():
            self._msg += f"\tbody: {self._response.request.read()}\n"
        else:
            self._msg += f"\tbody:\n"
        return self

    def add_response_info(self):
        """
        добавляет информацию о содержимом тела ответа
        """
        self._msg += f"Response body:\n\t{self._response.content}\n"
        return self

    def add_error_info(self, text):
        if text:
            self._msg += f"\n{text}\n"
        else:
            self._msg += "\n"
        return self

    def get_message(self):
        return self._msg


class BodyLogMsg(LogMsg):
    """
    Добавляет в логи результаты проверок тела ответа.
    """

    def __init__(self, response):
        super().__init__("IN RESPONSE BODY", response)

    def add_compare_result(self, diff):
        """
        добавляет информацию о результате сравнения полученного json с эталоном
        :param diff: словарь с данными полей, которые после сравнения имеют разные значения
        """
        self._msg += f"{self._where} in json following field didn't match with reference:\n"
        for key, value in diff.items():
            self._msg += f"key: {value['path']}\n\t\texpected: {value['expected']} \n\t\tactual: {value['actual']}\n"
        return self


class CodeLogMsg(LogMsg):
    """
    Добавляет в логи результаты проверки кода ответа.
    """
    def __init__(self, response):
        super().__init__('IN RESPONSE CODE', response)

    def add_compare_result(self, exp, act):
        """
        добавляет информацию об ожидаемом и полученной коде
        :param exp: ожидаемый код
        :param act: полученный код
        """
        self._msg += f"{self._where} \n\texpected code: {exp}\n\tactual code: {act}\n"
        return self


class BodyValueLogMsg(LogMsg):
    def __init__(self, response):
        super().__init__('IN RESPONSE BODY', response)

    def add_compare_result(self, exp, act):
        """
        добавляет информацию о сравнении значений в теле ответа
        :param exp: ожидаемое значение
        :param act: полученное значение
        """
        self._msg += f"\texptected: {exp}\n\tactual: {act}\n"
        return self


def assert_status_code(response, expected_code):
    """
    сравнивает код ответа от сервера с ожидаемым
    :param response: полученный от сервера ответ
    :param expected_code: ожидаемый код ответа
    :raises AssertionError: если значения не совпали
    """
    assert expected_code == response.status_code, CodeLogMsg(response) \
        .add_compare_result(expected_code, response.status_code) \
        .add_request_url() \
        .add_response_info() \
        .get_message()


def assert_schema(response, model: Type[BaseModel]):
    """
    проверяет тело ответа на соответствие его схеме механизмами pydantic
    :param response: ответ от сервера
    :param model: модель, по которой будет проверяться схема json
    :raises ValidationError: если тело ответа не соответствует схеме
    """
    body = response.json()
    if isinstance(body, list):
        for item in body:
            model.model_validate(item, strict=True)
    else:
        model.model_validate(body, strict=True)


def assert_left_in_right_json(response, exp_json, actual_json):
    """
    проверяет, что все значения полей exp_json равны значениям полей в actual_json
    :param response: полученный ответ от сервера
    :param exp_json: ожидаемый эталонный json
    :param actual_json: полученый json
    :raises AssertionError: если в exp_json есть поля со значениями, которые отличаются или которых нет в actual_json
    """
    root = 'root:' if isinstance(actual_json, list) else ''
    compare_res = compare_json_left_in_right(exp_json, actual_json, key=root, path=root)
    assert not compare_res, BodyLogMsg(response) \
        .add_compare_result(compare_res) \
        .add_request_url() \
        .add_response_info() \
        .get_message()




