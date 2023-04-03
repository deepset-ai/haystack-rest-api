# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from canals import load_pipelines
from haystack import __version__

from rest_api.config import DEFAULT_PIPELINES


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)


app = None
OPENAPI_TAGS = [
    {"name": "about", "description": "Check the app's status"},
    {"name": "pipelines", "description": "Operations on Pipelines: list, warmup, run, etc..."},
    {"name": "files", "description": "Operations on files: upload, dowload, list, etc..."},
]


def get_app(debug: bool = False, pipelines_path: Optional[Path] = None) -> None:
    global app  # pylint: disable=global-statement
    if not app:    
        app = FastAPI(
            title="Haystack",
            debug=debug,
            version=__version__,
            root_path="/",
            openapi_tags=OPENAPI_TAGS,
        )
        app.pipelines = load_pipelines(pipelines_path or DEFAULT_PIPELINES)

        from rest_api.routers import pipelines, about, files

        app.include_router(pipelines.router, tags=["pipelines"])
        app.include_router(files.router, tags=["files"])
        app.include_router(about.router, tags=["about"])

        app.add_exception_handler(HTTPException, http_error_handler)

    return app
