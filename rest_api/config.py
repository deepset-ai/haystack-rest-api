# SPDX-FileCopyrightText: 2022-present deepset GmbH <info@deepset.ai>
#
# SPDX-License-Identifier: Apache-2.0
import os
from pathlib import Path

DEFAULT_PIPELINES = Path(
    os.getenv("HAYSTACK_REST_API_PIPELINES_PATH", Path(__file__).parent / "pipelines" / "default.json")
)
FILE_UPLOAD_PATH = Path(os.getenv("HAYSTACK_REST_API_FILE_UPLOAD_PATH", Path(__file__).parent / "files"))
