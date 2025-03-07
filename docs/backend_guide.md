# Indexing Service Documentation

## Overview
The **Indexing Service** is responsible for creating embeddings from textual data using a **Hugging Face Sentence Transformer** model and storing these embeddings efficiently for fast retrieval. The service processes text fields from a dataset, encodes them into high-dimensional vectors, and stores both the embeddings and metadata for later use in a search engine.

## Features
- **Efficient text embedding** using `sentence-transformers`.
- **Batch processing** of documents to optimize memory and disk usage.
- **Metadata storage** for retrieval and validation.
- **Index validation** to ensure consistency of stored embeddings.

---

## Installation
To use this service, install the required dependencies:

```bash
pip install sentence-transformers numpy
```

Ensure that `backend.app.services.data_loader` contains the `Document` class definition.

---

## Class: `IndexingService`

### **Constructor: `__init__()`**
```python
IndexingService(model_name: str, index_dir: str = "./index", batch_size: int = 25000, field_to_index: str = "title")
```
#### **Parameters:**
- `model_name` *(str)*: The Hugging Face model name for text embedding.
- `index_dir` *(str, optional)*: The directory where index files are stored. Default is `./index`.
- `batch_size` *(int, optional)*: Number of embeddings stored per file. Default is `25000`.
- `field_to_index` *(str, optional)*: The text field in metadata to encode. Default is `title`.

#### **Functionality:**
- Loads the specified **sentence-transformers** model.
- Creates the index directory if it doesn’t exist.

---

### **Method: `create_embeddings()`**
```python
create_embeddings(documents: List[dict]) -> None
```
#### **Parameters:**
- `documents` *(List[dict])*: A list of `Document` objects containing text data.

#### **Functionality:**
1. Extracts text from the specified `field_to_index` in each document.
2. Filters out documents missing the indexed field.
3. Converts the text into dense embeddings using the `SentenceTransformer` model.
4. Stores embeddings in **NumPy (.npy) format**.
5. Saves metadata in **JSON format** for lookup and retrieval.
6. Logs progress and storage details for each batch processed.

#### **Example Usage:**
```python
indexing_service = IndexingService(model_name="sentence-transformers/all-MiniLM-L6-v2")
documents = [Document(title="AI in Healthcare"), Document(title="Quantum Computing Basics")]
indexing_service.create_embeddings(documents)
```

---

### **Method: `_validate_index()`**
```python
_validate_index() -> None
```
#### **Functionality:**
1. Scans the index directory for **embedding (.npy) and metadata (.json) files**.
2. Loads each pair and verifies that the number of stored embeddings matches the metadata count.
3. Logs inconsistencies if found.
4. Ensures alignment between **vector and metadata storage**.

---

## Indexing Output Structure
The embeddings and metadata are stored as:
```bash
./index/
    ├── embeddings_1.npy     # First batch of embeddings
    ├── metadata_1.json      # Corresponding metadata
    ├── embeddings_2.npy     # Second batch of embeddings
    ├── metadata_2.json      # Corresponding metadata
```

Each JSON metadata file contains an array of:
```json
[
    {
        "id": 0,
        "title": "AI in Healthcare",
        "metadata": { "source": "Wikipedia", "date": "2024-02-22" }
    },
    {
        "id": 1,
        "title": "Quantum Computing Basics",
        "metadata": { "source": "Research Paper", "date": "2023-11-10" }
    }
]
```

---

## **Best Practices**
- Use a **GPU** if processing large datasets to speed up encoding.
- Ensure that `field_to_index` exists in all documents to avoid data loss.
- Periodically run `_validate_index()` to check for inconsistencies.
- Store **embeddings and metadata in cloud storage** for distributed applications.

---

## **Future Enhancements**
- Add **FAISS or ChromaDB integration** for real-time search.
- Support **multiple fields** per document (e.g., title + content).
- Implement **incremental indexing** to update stored embeddings without reprocessing all data.

This indexing service is designed to be modular and efficient, making it a powerful foundation for **semantic search applications**. 🚀

