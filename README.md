# uitWiki Chatbot Service by Hien and Hai 😎

## How to run the project
Install the dependencies
```console
$ uv sync
```

Install the pre-commit hooks
```console
$ uv run pre-commit install
```

Create .env file and fill in the necessary information
```console
$ touch .env
```

Run the project with docker
```console
$ docker compose up
```
Run the project with uvicorn
```console
$ uv run fastapi dev
```