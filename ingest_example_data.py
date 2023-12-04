import glob
import requests


def ingest_example_data():
    """
    Call the file-upload endpoint with all the text files in the example-data folder.
    """
    for txt_file in glob.glob("example_data/*.txt"):
        print(txt_file)
        with open(txt_file, "rb") as f:
            r = requests.post(url="http://127.0.0.1:8000/file-upload", files={"files": f})
            print(r.json())


if __name__ == "__main__":
    ingest_example_data()
