> [!WARNING]
> This repository contained examples to show how to serve Haystack pipelines behind a rest api.
> Since then we introduced [Hayhooks](https://github.com/deepset-ai/hayhooks/) which offers this
> functionality explicitly and comprehensively.

# haystack-rest-api

This repository contains a simple Haystack RAG application with a REST API for indexing and querying purposes.

The application includes two containers:
- An Elasticsearch container
- A REST API container: built on FastAPI, this container integrates the Haystack logic and uses pipelines for indexing and querying. You can look at the [pipelines YAML files](./src/pipelines/) to see how the application is configured.

You can find more information in the [Haystack documentation](add a link when availaible).

## Getting started
Before you begin, make sure you have Python and Docker installed on your system.

- Clone this repository.
- Set the `OPENAI_API_KEY` environment variable following the instructions [here](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety#h_a1ab3ba7b2).
- Spin up the multi-container application (Elasticsearch + REST API) using Docker Compose: 
    ```bash
    docker-compose up -d
    ```
- Verify that the REST API is ready by running 
  ```bash
  curl http://localhost:8000/ready
  ```
  You should get `true` as a response.
- You can also check REST API interactive documentation at http://localhost:8000/docs.

## Indexing
To populate the application with example data about Oceanian countries, run the following script:
```bash
python ingest_example_data.py
```

You can also index your own text files using the `file-upload` endpoint:
```bash
curl -X 'POST' \
'http://localhost:8000/file-upload?keep_files=false' \
-H 'accept: application/json' \
-H 'Content-Type: multipart/form-data' \
-F 'files=@YOUR-TEXT-FILE.txt;type=text/plain'
```

## Querying
Use the query endpoint.
For example, to query the application with the question "Who are Torres Strait Islanders?", run:
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/query?query=Who%20are%20Torres%20Strait%20Islanders%3F' \
  -H 'accept: application/json'
```

You should get a response similar to the following:
```json
{
  "answer_builder": {
    "answers": [
      {
        "data": "Torres Strait Islanders are ethnically Melanesian people who obtained their livelihood from seasonal horticulture and the resources of their reefs and seas.",
        "query": "Who are Torres Strait Islanders?",
        "metadata": {
          "model": "gpt-3.5-turbo-0613",
          "index": 0,
          "finish_reason": "stop",
          "usage": {
            "prompt_tokens": 727,
            "completion_tokens": 29,
            "total_tokens": 756
          }
        },
        "documents": ["..."]
        }
    ]
  }
}
```

## Customization
This repository serves as a practical example of building your own Haystack application with a REST API.
For more information and guidance, refer to the [Haystack documentation](add a link when availaible).

