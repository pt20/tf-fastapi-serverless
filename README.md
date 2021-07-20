# tf-fastapi-serverless

## setup

following commands will set up virtual environment and `get_started.sh` will install dependencies.

```bash
git clone git@github.com:pt20/tf-fastapi-serverless.git
cd tf-fastapi-serverless
./get_started.sh
```

## spinning up the server

```bash
python src/main.py
```

## testing the endpoint

Go to your browser at `http://0.0.0.0:8080` and you should see

```python
{"message": "Welcome from the API"}
```

Go to `http://localhost:8080/windturbines/cog?url=https://up42test.s3.amazonaws.com/aus_cogs/aus_id_2.tif` and wait for some time until you get a geojson feature collection as a response.
