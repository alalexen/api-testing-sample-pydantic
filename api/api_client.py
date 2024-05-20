import os
from httpx import Client, Response

from utilities.logger_utils import logger


class ApiClient(Client):
    """  Extension of the standard httpx client. """
    def __init__(self):
        super().__init__(base_url=f"https://{os.getenv('RESOURCE_URL')}")

    def request(self, method, url, **kwargs) -> Response:
        """ Extension of the httpx request method logic with added logging
        of the request type and its URL. Logging is enabled or disabled
        based on the .env file.

        :param method: the method we use (POST, GET, etc.)
        :param url: the path on the domain to which we send the request"""

        if eval(os.getenv("USE_LOGS")):
            logger.info(f'{method} {url}')
        return super().request(method, url, **kwargs)

