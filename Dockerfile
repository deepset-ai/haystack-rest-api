FROM python:3.10-slim

# installing git is only necessary because elasticsearch-haystack is not yet a package
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*


WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src /code/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]