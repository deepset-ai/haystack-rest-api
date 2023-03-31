# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import logging

import uvicorn
from haystack.preview.rest_api.app import get_app


if __name__ == "__main__":
    app = get_app()

    logger = logging.getLogger(__name__)

    logger.info("Open http://127.0.0.1:8000/docs to see the API Documentation.")
    logger.info(
        "Or just try it out directly: curl --request POST --url 'http://127.0.0.1:8000/query_pipeline/run' "
        '-H "Content-Type: application/json"  --data \'{"query": "Who is the father of Arya Stark?"}\''
    )

    uvicorn.run(app, host="0.0.0.0", port=8000)
