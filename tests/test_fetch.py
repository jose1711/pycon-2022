import asyncio
import json
import time
from functools import partial

import pytest
from pytest_httpserver import HTTPServer
from werkzeug import Response

from app import fetch, get_first_successful_request


@pytest.fixture
def httpserver1(httpserver_ssl_context, httpserver_listen_address):
    server = HTTPServer(host=HTTPServer.DEFAULT_LISTEN_HOST, port=7001, ssl_context=httpserver_ssl_context)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


@pytest.fixture
def httpserver2(httpserver_ssl_context, httpserver_listen_address):
    server = HTTPServer(host=HTTPServer.DEFAULT_LISTEN_HOST, port=7002, ssl_context=httpserver_ssl_context)
    server.start()
    yield server
    server.clear()
    if server.is_running():
        server.stop()


def slow_response(request, time_to_wait_seconds: float, status: int = 200) -> Response:
    time.sleep(time_to_wait_seconds)
    return Response(json.dumps({"time": time_to_wait_seconds}), status, content_type="application/json")


@pytest.mark.asyncio
async def test_successful_fetch(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_handler(partial(slow_response, time_to_wait_seconds=0.2))

    success, result = await fetch(0, httpserver.url_for("/foobar"))

    assert success
    assert {"time": 0.2} == result


@pytest.mark.asyncio
async def test_unsuccessful_fetch(httpserver: HTTPServer):
    httpserver.expect_request("/foobar").respond_with_handler(
        partial(slow_response, status=400, time_to_wait_seconds=0.2)
    )

    success, result = await fetch(0, httpserver.url_for("/foobar"))

    assert not success


@pytest.mark.asyncio
async def test_first_successful_requests(httpserver: HTTPServer, httpserver1, httpserver2):
    httpserver.expect_request("/foo").respond_with_handler(partial(slow_response, time_to_wait_seconds=0.8))
    httpserver1.expect_request("/foo").respond_with_handler(partial(slow_response, time_to_wait_seconds=0.2))
    httpserver2.expect_request("/foo").respond_with_handler(partial(slow_response, time_to_wait_seconds=0.4))

    unfinished_tasks = [
        asyncio.create_task(fetch(delay_seconds=0, url=httpserver.url_for("/foo"))),
        asyncio.create_task(fetch(delay_seconds=0, url=httpserver1.url_for("/foo"))),
        asyncio.create_task(fetch(delay_seconds=0, url=httpserver2.url_for("/foo"))),
    ]
    success, result = await get_first_successful_request(unfinished_tasks, timeout=None)

    assert success
    assert {"time": 0.2} == result


