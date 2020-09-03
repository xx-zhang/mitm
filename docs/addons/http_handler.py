# coding:utf-8
"""HTTP-specific events."""
import sys
from mitmproxy.http import HTTPFlow
from mitmproxy import ctx

sys.path.insert(0, '../')

from http_helper.parser import parse_http
from http_helper.conf import load_user_config
from opssdk.operate.kafka_helper import KafkaHelper

config = load_user_config()


class Events:
    def http_connect(self, flow: HTTPFlow):
        """
            An HTTP CONNECT request was received. Setting a non 2xx response on
            the flow will return the response to the client abort the
            connection. CONNECT requests and responses do not generate the usual
            HTTP handler events. CONNECT requests are only valid in regular and
            upstream proxy modes.
        """

    def requestheaders(self, flow: HTTPFlow):
        """
            HTTP request headers were successfully read. At this point, the body
            is empty.
        """

    def request(self, flow: HTTPFlow):
        """
            The full HTTP request has been read.
        """

    def responseheaders(self, flow: HTTPFlow):
        """
            HTTP response headers were successfully read. At this point, the body
            is empty.
        """

    def response(self, flow: HTTPFlow):
        """
            The full HTTP response has been read.
        """
        try:
            __msg = parse_http(flow)
            KafkaHelper(kafka_server=config.KAFKA_SERVER, topic=config.TOPIC).send(__msg)
        except Exception as e:
            from opssdk.xlogs import Log
            logger = Log(log_flag='mitm_main_run')
            logger.info(e)

    def error(self, flow: HTTPFlow):
        """
            An HTTP error has occurred, e.g. invalid server responses, or
            interrupted connections. This is distinct from a valid server HTTP
            error response, which is simply a response with an HTTP error code.
        """


addons = [
    Events()
]



