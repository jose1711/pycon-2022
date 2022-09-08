import asyncio
from http import HTTPStatus
from typing import TypeAlias

from aiohttp import ClientSession, ContentTypeError
from flask import Flask, jsonify, redirect, url_for, request
from werkzeug.exceptions import BadRequest, RequestTimeout

# Create the Flask application
app = Flask(__name__)

BLOOMREACH_SERVER = "https://exponea-engineering-assignment.appspot.com/api/work"


@app.route("/")
def hello():
    return redirect(url_for("smart_api_requester"))


Success: TypeAlias = bool


async def fetch() -> tuple[Success, dict]:
    async with ClientSession() as session:
        try:
            async with session.get(BLOOMREACH_SERVER) as response:
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


@app.get("/api/smart")
async def smart_api_requester():
    timeout_seconds = get_and_validate_timeout()
    try:
        success, result = await asyncio.wait_for(fetch(), timeout=timeout_seconds)
    except asyncio.TimeoutError:
        raise RequestTimeout()

    return jsonify(success=success, response=result)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8081)
