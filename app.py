import asyncio
import time
from http import HTTPStatus

from typing import TypeAlias

from aiohttp import ClientSession, ContentTypeError
from flask import Flask, jsonify, redirect, url_for, request
from werkzeug.exceptions import BadRequest, RequestTimeout

# Create the Flask application
app = Flask(__name__)

BLOOMREACH_SERVER = "https://exponea-engineering-assignment.appspot.com/api/work"

WAIT_BEFORE_NEXT_REQUEST_SECONDS = 0.3


@app.route("/")
def hello():
    return redirect(url_for("smart_api_requester"))


Success: TypeAlias = bool


async def fetch(delay_seconds: float, url: str = BLOOMREACH_SERVER) -> tuple[Success, dict]:
    time.sleep(delay_seconds)
    async with ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == HTTPStatus.OK:
                    try:
                        result_data = await response.json()
                    except ContentTypeError:
                        return False, {}

                    return True, result_data
                else:
                    return False, {}
        except Exception:
            # Catch any session error (e.g. timeout)
            return False, {}


def milliseconds_to_seconds(value: int) -> float:
    return value / 1000


def get_and_validate_timeout() -> None | float:
    timeout = request.args.get("timeout")
    if timeout is None:
        return timeout

    try:
        converted_timeout = milliseconds_to_seconds(int(timeout))
    except ValueError:
        raise BadRequest("Timeout has to be integer value.")

    if converted_timeout <= 0:
        raise BadRequest("Timeout has to be positive non zero value.")

    return converted_timeout


def out_of_time(timeout: None | float) -> bool:
    return timeout is not None and timeout <= 0


async def get_first_successful_request(unfinished_tasks: list[asyncio.Task], timeout: None | float):
    timeout_remaining = timeout

    while not out_of_time(timeout_remaining) and unfinished_tasks:
        start = time.monotonic()
        finished_tasks, unfinished_tasks = await asyncio.wait(
            unfinished_tasks, return_when=asyncio.FIRST_COMPLETED, timeout=timeout_remaining
        )

        for finished_task in finished_tasks:
            success, result = finished_task.result()
            if success:
                return success, result

        end = time.monotonic()
        timeout_remaining = timeout_remaining - (end - start) if timeout_remaining is not None else timeout_remaining

    for unfinished_task in unfinished_tasks:
        unfinished_task.cancel()

    if out_of_time(timeout_remaining):
        raise RequestTimeout()

    return False, {}


@app.get("/api/smart")
async def smart_api_requester():
    timeout_seconds = get_and_validate_timeout()
    unfinished_tasks = [
        asyncio.create_task(fetch(delay_seconds=0)),
        asyncio.create_task(fetch(delay_seconds=WAIT_BEFORE_NEXT_REQUEST_SECONDS)),
        asyncio.create_task(fetch(delay_seconds=WAIT_BEFORE_NEXT_REQUEST_SECONDS)),
    ]

    success, result = await get_first_successful_request(unfinished_tasks, timeout_seconds)

    return jsonify(success=success, result=result)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8081)
