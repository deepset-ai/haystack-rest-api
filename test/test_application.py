import glob
import requests


def test_application():
    # test status endpoint
    r = requests.get(url="http://127.0.0.1:8000/ready")
    assert r.status_code == 200
    assert r.text == "true"

    # test file-upload endpoint (indexing)
    for txt_file in glob.glob("example_data/*.txt"):
        with open(txt_file, "rb") as f:
            r = requests.post(
                url="http://127.0.0.1:8000/file-upload", files={"files": f}
            )

            json_response = r.json()
            assert "writer" in json_response
            assert json_response["writer"]["documents_written"] > 0

    # test query endpoint (RAG pipeline)
    query = "Who are Torres Strait Islanders?"
    r = requests.get(url="http://127.0.0.1:8000/query", params={"query": query})
    json_response = r.json()
    print(json_response)
    assert "answer_builder" in json_response

    assert "answers" in json_response["answer_builder"]
    answer = json_response["answer_builder"]["answers"][0]

    assert answer["query"] == query
    assert "data" in answer
    assert "metadata" in answer

    # check that the Documents have been correctly retrieved and used
    assert "documents" in answer
    assert len(answer["documents"]) > 0