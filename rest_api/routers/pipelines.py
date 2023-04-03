# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
from typing import Dict, Any, Optional

import logging
import time
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from canals import load_pipelines, Pipeline

from rest_api.config import DEFAULT_PIPELINES


logger = logging.getLogger(__name__)
router = APIRouter()
_pipelines: Dict[str, Pipeline] = {}


def get_pipelines(pipelines_path: Optional[Path] = None) -> Dict[str, Pipeline]:
    """
    Returns the pipelines used by this application. If pipelines are not loaded, loads them.
    """
    global _pipelines  # pylint: disable=global-statement
    if not _pipelines:
        _pipelines = load_pipelines(pipelines_path or DEFAULT_PIPELINES)
    return _pipelines


@router.get("/pipelines")
def list_pipelines():
    """
    List the names and metadata of all available pipelines.
    """
    return {pipeline_name: pipeline.metadata for pipeline_name, pipeline in get_pipelines().items()}


@router.post("/pipelines/warmup")
def warmup_all():
    """
    Warm up all pipelines.
    """
    for pipeline_name, pipeline in get_pipelines().items():
        start_time = time.time()
        pipeline.warm_up()
        logger.info(
            json.dumps(
                {"type": "warmup", "pipeline": pipeline_name, "time": f"{(time.time() - start_time):.2f}"}, default=str
            )
        )


@router.post("/pipelines/{pipeline_name}/warmup")
def warmup(pipeline_name: str):
    """
    Warm up the specified pipeline.
    """
    pipelines = get_pipelines()

    if not pipeline_name in pipelines.keys():
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline named '{pipeline_name}' not found. "
            f"Available pipelines: '{', '.join(pipelines.keys())}'",
        )
    pipeline = pipelines[pipeline_name]

    start_time = time.time()
    pipeline.warm_up()
    logger.info(
        json.dumps(
            {"type": "warmup", "pipeline": pipeline_name, "time": f"{(time.time() - start_time):.2f}"}, default=str
        )
    )


@router.post("/pipelines/{pipeline_name}/run")
def run(pipeline_name: str, data: Dict[str, Any], parameters: Dict[str, Dict[str, Any]], debug: bool = False):
    """
    Runs a pipeline. Provide the same values for `data` and `parameters` as you would in Canals or Haystack.

    If the pipeline needs files, first upload them with `POST /uploads`, then reference them with the
    path after upload within the REST API, for example as `/uploads/<filename>`.
    """
    pipelines = get_pipelines()
    if not pipeline_name in pipelines.keys():
        raise HTTPException(
            status_code=404,
            detail=f"Pipeline named '{pipeline_name}' not found. "
            f"Available pipelines: {', '.join(pipelines.keys())}",
        )
    pipeline = pipelines[pipeline_name]

    for parameters_for_node in parameters.keys():
        try:
            pipeline.get_node(parameters_for_node)
        except ValueError as exc:
            raise HTTPException(
                status_code=404,
                detail=f"Node named '{parameters_for_node}' not found. "
                f"Available nodes for '{pipeline_name}': {', '.join(pipeline.graph.nodes)}",
            ) from exc

    start_time = time.time()
    try:
        result = pipeline.run(data=data, parameters=parameters, debug=debug)
        logger.info(
            json.dumps(
                {
                    "type": "run",
                    "pipeline": pipeline_name,
                    "data": data,
                    "parameters": parameters,
                    "debug": debug,
                    "response": result,
                    "time": f"{(time.time() - start_time):.2f}",
                },
                default=str,
            )
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline '{pipeline_name}' failed. Exception: {exc}") from exc
