import os
from haystack.preview import Pipeline
from haystack.preview.components.preprocessors import (
    DocumentCleaner,
    TextDocumentSplitter,
)
from haystack.preview.components.writers import DocumentWriter
from haystack.preview.components.writers.document_writer import DuplicatePolicy
from haystack.preview.components.file_converters import PyPDFToDocument

from haystack.preview.components.builders.prompt_builder import PromptBuilder
from haystack.preview.components.generators import GPTGenerator
from haystack.preview.components.builders.answer_builder import AnswerBuilder

from elasticsearch_haystack import ElasticsearchDocumentStore
from elasticsearch_haystack.bm25_retriever import ElasticsearchBM25Retriever

document_store = ElasticsearchDocumentStore(
    hosts=os.getenv("DOCUMENTSTORE_PARAMS_HOST", "http://localhost:9200")
)


def create_indexing_pipeline():
    indexing = Pipeline()
    indexing.add_component("converter", PyPDFToDocument())
    indexing.add_component("cleaner", DocumentCleaner())
    indexing.add_component(
        "splitter", TextDocumentSplitter(split_by="word", split_length=200)
    )
    indexing.add_component(
        "writer",
        DocumentWriter(document_store=document_store, policy=DuplicatePolicy.SKIP),
    )
    indexing.connect("converter", "cleaner")
    indexing.connect("cleaner", "splitter")
    indexing.connect("splitter", "writer")

    return indexing


def create_rag_pipeline():
    prompt_template = """
    Given these documents, answer the question.\nDocuments: 
    {% for doc in documents %}
        {{ doc.text }} 
    {% endfor %}

    \nQuestion: {{question}}
    \nAnswer:
    """

    rag = Pipeline()
    rag.add_component(
        "retriever", ElasticsearchBM25Retriever(document_store=document_store, top_k=5)
    )
    rag.add_component("prompt_builder", PromptBuilder(template=prompt_template))
    rag.add_component("llm", GPTGenerator(api_key=os.environ.get("OPENAI_API_KEY")))
    rag.add_component("answer_builder", AnswerBuilder())

    rag.connect("retriever", "prompt_builder.documents")
    rag.connect("prompt_builder", "llm")
    rag.connect("llm.replies", "answer_builder.replies")
    rag.connect("llm.metadata", "answer_builder.metadata")
    rag.connect("retriever", "answer_builder.documents")

    return rag

