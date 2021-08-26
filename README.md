# tf-fastapi-serverless

## setup

following commands will set up virtual environment and `get_started.sh` will install dependencies.

```bash
git clone git@github.com:pt20/tf-fastapi-serverless.git
cd tf-fastapi-serverless
./get_started.sh
```

## spinning up the services

Make sure to have docker installed on your system

```bash
docker-compose up --build
```

## testing the endpoint

Go to your browser at `http://0.0.0.0:8004` and you should see

```python
{"message": "Sometimes the wheel turns slowly, but it turns."}
```

`http://0.0.0.0:8004/docs` will take you to interactive API documentation. You can try the endpoints from there as well.
