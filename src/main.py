from typing import List, Optional
from pathlib import Path
import os
import uuid

from fastapi import FastAPI, UploadFile, File
from haystack.preview import Pipeline

# Needed to load the Pipeline without errors (https://github.com/deepset-ai/haystack/issues/6186)
from haystack.preview.components.preprocessors import DocumentCleaner, TextDocumentSplitter
from haystack.preview.components.file_converters import PyPDFToDocument
from haystack.preview.components.builders.answer_builder import AnswerBuilder
from haystack.preview.components.builders.prompt_builder import PromptBuilder
from haystack.preview.components.generators import GPTGenerator
from haystack.preview.components.writers import DocumentWriter
from elasticsearch_haystack.document_store import ElasticsearchDocumentStore
from elasticsearch_haystack.bm25_retriever import ElasticsearchBM25Retriever

app = FastAPI(title="My Haystack RAG API")

# Load the pipelines from the YAML files
with open("./src/pipelines/indexing_pipeline.yaml", "rb") as f:
    indexing_pipeline = Pipeline.load(f)
with open("./src/pipelines/rag_pipeline.yaml", "rb") as f:
    rag_pipeline = Pipeline.load(f)

# Create the file upload directory if it doesn't exist
FILE_UPLOAD_PATH = os.getenv(
    "FILE_UPLOAD_PATH", str((Path(__file__).parent.parent / "file-upload").absolute())
)
Path(FILE_UPLOAD_PATH).mkdir(parents=True, exist_ok=True)


@app.get("/ready")
def check_status():
    """
    This endpoint can be used during startup to understand if the
    server is ready to take any requests, or is still loading.

    The recommended approach is to call this endpoint with a short timeout,
    like 500ms, and in case of no reply, consider the server busy.
    """
    return True


@app.post("/file-upload")
def upload_files(
    files: List[UploadFile] = File(...), keep_files: Optional[bool] = False
):
    """
    Upload a list of files to be indexed.

    Note: files are removed immediately after being indexed. If you want to keep them, pass the
    `keep_files=true` parameter in the request payload.
    """

    file_paths: list = []

    for file_to_upload in files:
        try:
            file_path = (
                Path(FILE_UPLOAD_PATH) / f"{uuid.uuid4().hex}_{file_to_upload.filename}"
            )
            with file_path.open("wb") as fo:
                fo.write(file_to_upload.file.read())
            file_paths.append(file_path)
        finally:
            file_to_upload.file.close()

    result = indexing_pipeline.run({"converter": {"sources": file_paths}})

    # Clean up indexed files
    if not keep_files:
        for p in file_paths:
            p.unlink()

    return result


@app.get("/query")
def ask_rag_pipeline(query: str):
    """
    Ask a question to the RAG pipeline.
    """
    result = rag_pipeline.run(
        {
            "retriever": {"query": query},
            "prompt_builder": {"question": query},
            "answer_builder": {"query": query},
        }
    )

    return result
