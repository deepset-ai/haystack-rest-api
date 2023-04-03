import os

import pytest

import rest_api.routers.files as files_router


@pytest.fixture(autouse=True)
def upload_path(monkeypatch, tmp_path):
    monkeypatch.setattr(files_router, "FILE_UPLOAD_PATH", tmp_path)


def test_list_files_empty(client):
    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == []


def test_list_files_non_existing_dir(client):
    response = client.get(url="/files/non_existing")
    assert 404 == response.status_code
    response_json = response.json()
    assert response_json == {"errors": ["'non_existing' does not exist."]}


def test_list_files_only_files_in_root(client, tmp_path):
    with open(tmp_path / "test.txt", "w") as test_file:
        test_file.write("Hello!")

    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == ["test.txt"]

    with open(tmp_path / "test2.txt", "w") as test_file:
        test_file.write("Hello!")

    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert len(response_json) == 2
    assert set(response_json) == {"test.txt", "test2.txt"}


def test_list_empty_folders(client, tmp_path):
    os.makedirs(tmp_path / "test_dir")

    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == ["test_dir"]

    os.makedirs(tmp_path / "test_dir_2")

    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert len(response_json) == 2
    assert set(response_json) == {"test_dir", "test_dir_2"}


def test_list_empty_folders_and_root_level_files(client, tmp_path):
    os.makedirs(tmp_path / "test_dir")
    with open(tmp_path / "test.txt", "w") as test_file:
        test_file.write("")

    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert set(response_json) == {"test.txt", "test_dir"}


def test_list_folders_with_files(client, tmp_path):
    os.makedirs(tmp_path / "test_dir")
    with open(tmp_path / "test_dir" / "test.txt", "w") as test_file:
        test_file.write("")

    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == ["test_dir"]

    response = client.get(url="/files/test_dir")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == ["test.txt"]


def test_list_nested_folders(client, tmp_path):
    os.makedirs(tmp_path / "test_dir")
    os.makedirs(tmp_path / "test_dir" / "test_dir_2")
    with open(tmp_path / "test_dir" / "test_dir_2" / "test.txt", "w") as test_file:
        test_file.write("")

    response = client.get(url="/files")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == ["test_dir"]

    response = client.get(url="/files/test_dir")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == ["test_dir_2"]

    response = client.get(url="/files/test_dir/test_dir_2")
    assert 200 == response.status_code
    response_json = response.json()
    assert response_json == ["test.txt"]


def test_download_nonexisting_file(client):
    response = client.get(url="/files/non_existing.txt")
    assert 404 == response.status_code
    response_json = response.json()
    assert response_json == {"errors": ["'non_existing.txt' does not exist."]}


def test_download_nonexisting_folder(client):
    response = client.get(url="/files/test/non_existing.txt")
    assert 404 == response.status_code
    response_json = response.json()
    assert response_json == {"errors": ["'test/non_existing.txt' does not exist."]}


def test_download_file_in_root(client, tmp_path):
    with open(tmp_path / "test.txt", "w") as test_file:
        test_file.write("test file")

    response = client.get(url="/files/test.txt")
    assert 200 == response.status_code

    assert response.content.decode("utf-8") == "test file"


def test_download_file_in_nested_folder(client, tmp_path):
    os.makedirs(tmp_path / "test1" / "test2")
    with open(tmp_path / "test1" / "test2" / "test.txt", "w") as test_file:
        test_file.write("test file")

    response = client.get(url="/files/test1/test2/test.txt")
    assert 200 == response.status_code

    assert response.content.decode("utf-8") == "test file"


def test_upload_file_in_root(client, tmp_path):
    with open(tmp_path / "temp", "w") as test_file:
        test_file.write("test file")

    response = client.post(
        url="/files/test.txt", files={"file": ("filename", open(tmp_path / "temp", "rb"), "text/plain")}
    )
    assert 200 == response.status_code

    with open(tmp_path / "test.txt", "r") as test_file:
        test_file.read() == "test file"


def test_upload_file_in_nested_folder(client, tmp_path):
    with open(tmp_path / "temp", "w") as test_file:
        test_file.write("test file")

    response = client.post(
        url="/files/test1/test2/test.txt",
        files={"file": ("filename", open(tmp_path / "temp", "rb"), "text/plain")},
    )
    assert 200 == response.status_code

    with open(tmp_path / "test1" / "test2" / "test.txt", "r") as test_file:
        test_file.read() == "test file"
