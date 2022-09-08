# Starting

> **_BRANCH:_**  You can start from the branch `start`.
>
> `git checkout start`

We get very basic skeleton of our application without the real implementation. In our workshop we will to finish the
implementation so all the cases in our assignment is covered.

## Setting up the python environment

1. Create python virtual environment
    ```
    python3.10 -m venv venv
    ```
2. Activate python virtual environment
    ```
    source venv/bin/activate
    ```
3. Install requirements
    ```
    pip install -r requirements.txt
    ```

> **_QUESTION:_** Why is good to create and use the virtual environment?

<details>
  <summary>Click on me for the answer!</summary>

Using the virtual environment allows you to a have different dependencies for each project. This means you to have
different version of python packages. In addition to that you can easily add or remove a package without affecting other
projects.

</details>

## Test the application

After successfully setting your environment you, should be able to start your application.

    ```
    python app.py
    ```

> **_QUESTION:_**  For running our server we picked web framework Flask. Do you know any python alternatives to Flask?
> Does this alternative have any advantages/disadvantages compared to Flask?
<details>
  <summary>Click on me for the answer!</summary>

There are many python web frameworks, e.g. FastAPI, Django, Starlette and so on. Each of them have different
advantages/disadvantages, for example Starlette is ideal for async programs. FastAPI also uses Starlette, but also
provide more functionality and so on. I picked flask, because we use it in Bloomreach. 

</details>

