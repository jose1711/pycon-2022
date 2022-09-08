# Finish the implementation

> **_BRANCH:_**  You can start from the branch `timeout`.
>
> `git checkout timeout`

Till now, we were able to trigger the first request and if it has not finished in the specified time, we will raise the
timeout error.

Now, we are going to implement second and third request. Those two request should be triggered after 300ms from the
first one. In addition, they should be triggered at once, and we should return the first successful. If the first
request finish after 300ms, but before the second and third, we will return it.

## Implementing the second and third request

As you might guess, all our requests will be done asynchronously. We need to secure that second and third request is
triggered after 300ms after the first one.

1. Postpone the fetch by specific time.
    ```python
    async def fetch(delay_seconds: float) -> tuple[Success, dict]:
        await asyncio.sleep(delay_seconds)
    ...
    ```
   > **_QUESTION:_** Why we used `asyncio.sleep` and no classic one time.sleep?
   <details>
   <summary>Click on me for the answer!</summary>

   When time.sleep(x) is called, it will block the entire execution of the script, and it will be put on hold, just
   frozen, doing nothing. But when you call await asyncio.sleep(x), it will ask the event loop to run something else
   while your await statement finishes its execution.
   </details>

2. Create tasks.
    ```python
   @app.get("/api/smart")
   async def smart_api_requester():
       timeout_seconds = get_and_validate_timeout()
       unfinished_tasks = [
           asyncio.create_task(fetch(delay_seconds=0)),
           asyncio.create_task(fetch(delay_seconds=WAIT_BEFORE_NEXT_REQUEST_SECONDS)),
           asyncio.create_task(fetch(delay_seconds=WAIT_BEFORE_NEXT_REQUEST_SECONDS)),
       ]
       ...
    ```
   As we can see, we created 3 tasks. First request won't be delayed, the second and third one will be delayed for the
   time specified in the assignment.
3. Execute those task.
   ```python
   def out_of_time(timeout: None | float) -> bool:
       return timeout is not None and timeout <= 0
   
   
   @app.get("/api/smart")
   async def smart_api_requester():
       timeout_seconds = get_and_validate_timeout()
       unfinished_tasks = [
           asyncio.create_task(fetch(delay_seconds=0)),
           asyncio.create_task(fetch(delay_seconds=WAIT_BEFORE_NEXT_REQUEST_SECONDS)),
           asyncio.create_task(fetch(delay_seconds=WAIT_BEFORE_NEXT_REQUEST_SECONDS)),
       ]
       timeout_remaining = timeout_seconds
   
       while not out_of_time(timeout_remaining) and unfinished_tasks:
           start = time.monotonic()
           finished_tasks, unfinished_tasks = await asyncio.wait(
               unfinished_tasks, return_when=asyncio.FIRST_COMPLETED, timeout=timeout_remaining
           )
   
           for finished_task in finished_tasks:
               success, result = finished_task.result()
               if success:
                   return jsonify(success=success, response=result)
   
           end = time.monotonic()
           timeout_remaining = timeout_remaining - (end - start) if timeout_remaining is not None else timeout_remaining
   
       if out_of_time(timeout_remaining):
           raise RequestTimeout()
   
       return jsonify(success=False, response={})
   ```
   We wait for the first task to finish. However, this task could finish with an error or with not successful respond.
   Therefor, we need to repeat our loop till we don't receive first successful response, or we are not out of the time.

> **_QUESTION:_** There is still one problem in how we handle our tasks, can you spot the problem?
<details>
<summary>Click on me for the answer!</summary>

If we got successful response, we will return it, but there might still be two tasks in the event loop.
As we don't need the result from them, we can cancel them.

4. Cancel unfinished tasks
   ```python
   ...      
   for unfinished_task in unfinished_tasks:
       unfinished_task.cancel()
          
   if out_of_time(timeout_remaining):
       raise RequestTimeout()
   ...
   ```

</details>