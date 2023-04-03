# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from haystack import __version__


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    """
    Converts HTTP errors into JSON responses carrying the error messages.
    """
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)


app: Optional[FastAPI] = None
OPENAPI_TAGS = [
    {"name": "about", "description": "Check the app's status"},
    {"name": "pipelines", "description": "Operations on Pipelines: list, warmup, run, etc..."},
    {"name": "files", "description": "Operations on files: upload, dowload, list, etc..."},
]


def get_app(debug: bool = False) -> FastAPI:
    """
    Returns the FastAPI object. If not existing, initializes it.
    """
    global app  # pylint: disable=global-statement
    if not app:
        app = FastAPI(
            title="Haystack",
            debug=debug,
            version=__version__,
            root_path="/",
            openapi_tags=OPENAPI_TAGS,
        )

        from rest_api.routers.pipelines import router as pipelines_router  # pylint: disable=C0415
        from rest_api.routers.files import router as files_router  # pylint: disable=C0415
        from rest_api.routers.about import router as about_router  # pylint: disable=C0415

        app.include_router(pipelines_router, tags=["pipelines"])
        app.include_router(files_router, tags=["files"])
        app.include_router(about_router, tags=["about"])

        app.add_exception_handler(HTTPException, http_error_handler)

    return app
