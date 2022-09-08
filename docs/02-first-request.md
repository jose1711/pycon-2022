# First request

> **_BRANCH:_**  You can start from the branch `start`.
>
> `git checkout start`

It is always good to split complex problem to multiple smaller one. We will do the same thing with our assignment. So,
let's now focus only on the first request.

## Triggering first request

To get the response from our testing server we can use python library `requests`.

1. Import the `requests` library.

    ```python
    import requests
    ```

2. Get the response from our testing server.

    ```python
    @app.get("/api/smart")
    def smart_api_requester():
        response = requests.get(BLOOMREACH_SERVER)
    ```
3. Check the status code of the response.
    ```python
    @app.get("/api/smart")
    def smart_api_requester():
        response = requests.get(BLOOMREACH_SERVER)
        if response.status_code == HTTPStatus.OK:
            pass
    ```
4. Based on the status code, return a response from our endpoint .
    ```python
   @app.get("/api/smart")
   def smart_api_requester():
       response = requests.get(BLOOMREACH_SERVER)
   
       if response.status_code == HTTPStatus.OK:
           return jsonify(success=True, response=response.json())
       else:
           return jsonify(success=False)
    ```

