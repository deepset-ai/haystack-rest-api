# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Optional
import os
import logging
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

from rest_api.config import FILE_UPLOAD_PATH


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/files")
@router.post("/files/{path:path}")
def upload_file(path: Optional[Path] = None, file: UploadFile = File(...)):
    """
    You can use this endpoint to upload a file. It gets stored in an internal folder, ready
    to be used by Pipelines. The folder where the files are stored can be configured
    through the env var `HAYSTACK_REST_API_FILE_UPLOAD_PATH` and defaults to the `files/` folder
    under the installation path.

    You can reference them with the path after upload within the REST API,
    for example as `/files/<path>/<filename>`.
    """
    full_path: Path
    if path:
        full_path = FILE_UPLOAD_PATH / path
    else:
        full_path = FILE_UPLOAD_PATH / (file.filename or "")

    if not os.path.exists(full_path.parent):
        logger.info("Creating %s", full_path.parent.absolute())
        os.makedirs(full_path.parent)

    if os.path.exists(Path(full_path)):
        raise HTTPException(
            status_code=409, detail="A file with the same name already exist. Rename it and try again."  # 409 Conflict
        )
    try:
        file_path = Path(full_path)
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()


@router.get("/files")
@router.get("/files/{path:path}")
def list_files(path: Path = Path(".")):
    """
    Browse the uploaded files.

    If the path points to a folder, it returns a list of what it contains (folders and filenames).
    If the path points to a file, it serves the file.
    """
    if not os.path.exists(FILE_UPLOAD_PATH):
        logger.info("Creating %s", FILE_UPLOAD_PATH.absolute())
        os.makedirs(FILE_UPLOAD_PATH)

    full_path = FILE_UPLOAD_PATH / path

    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail=f"'{full_path.relative_to(FILE_UPLOAD_PATH)}' does not exist.")

    if os.path.isfile(full_path):
        return FileResponse(full_path)

    if os.path.isdir(full_path):
        return [filename.name for filename in list(Path(full_path).iterdir())]

    raise HTTPException(
        status_code=500, detail=f"'{full_path.relative_to(FILE_UPLOAD_PATH)}' is neither a file nor a directory."
    )
