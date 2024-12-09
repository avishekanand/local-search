import os
import json
import csv
from typing import List, Dict
import zipfile
import shutil
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Document:
    def __init__(self, **kwargs):
        """
        Generic document class. Fields can be dynamically assigned.
        """
        for key, value in kwargs.items():
            setattr(self, key, value)

def extract_zip(file_path: str, extract_to: str) -> List[str]:
    """
    Extracts a ZIP file to the specified directory and returns a list of file paths.
    """
    try:
        if not zipfile.is_zipfile(file_path):
            raise ValueError(f"{file_path} is not a valid ZIP file")
        logger.debug(f"Extracting ZIP file: {file_path} to {extract_to}")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        extracted_files = [os.path.join(extract_to, f) for f in os.listdir(extract_to)]
        logger.debug(f"Files extracted: {extracted_files}")
        return extracted_files
    except Exception as e:
        logger.error(f"Error extracting ZIP file '{file_path}': {e}")
        raise

def load_metadata_fields(metadata_file: str) -> List[str]:
    """
    Loads metadata field mappings from a CSV file.
    Returns a list of field names in the same order as in the metadata file.
    """
    try:
        with open(metadata_file, "r") as f:
            reader = csv.reader(f)
            fields = next(reader)  # Extract the first row as field names
        logger.debug(f"Metadata fields loaded: {fields}")
        return fields
    except Exception as e:
        logger.error(f"Error reading metadata file '{metadata_file}': {e}")
        raise ValueError(f"Error reading metadata file '{metadata_file}': {e}")


def load_documents_from_csv(data_file: str, metadata_fields: List[str]) -> List[Document]:
    """
    Loads documents from a CSV data file, mapping the columns using metadata fields.
    """
    documents = []
    try:
        with open(data_file, "r") as f:
            reader = csv.reader(f)
            for row_num, row in enumerate(reader, start=1):
                # Map metadata fields to row values
                document_data = {metadata_fields[i]: row[i] if i < len(row) else None for i in range(len(metadata_fields))}
                documents.append(Document(**document_data))
                if row_num % 1000 == 0:  # Log progress every 1000 rows
                    logger.debug(f"{row_num} rows processed from {data_file}")
        logger.info(f"Total documents loaded from {data_file}: {len(documents)}")
        return documents
    except Exception as e:
        logger.error(f"Error loading documents from CSV file '{data_file}': {e}")
        raise ValueError(f"Error loading documents from CSV file '{data_file}': {e}")

def load_metadata_fields(metadata_file: str) -> List[str]:
    """
    Loads metadata field mappings from a CSV file.
    Returns a list of field names in the same order as in the metadata file.
    """
    try:
        with open(metadata_file, "r") as f:
            reader = csv.reader(f)
            fields = next(reader)  # Extract the first row as field names
        logger.debug(f"Metadata fields loaded: {fields}")
        return fields
    except Exception as e:
        logger.error(f"Error reading metadata file '{metadata_file}': {e}")
        raise ValueError(f"Error reading metadata file '{metadata_file}': {e}")


def load_documents(file_path: str, metadata_file: str, temp_dir: str = "./temp") -> List[Document]:
    """
    Handles loading documents from a CSV data file using metadata for field mapping.
    Supports direct file processing or ZIP extraction.
    """
    # Load metadata field names
    logger.debug(f"Loading metadata from file: {metadata_file}")
    metadata_fields = load_metadata_fields(metadata_file)

    documents = []

    try:
        # Handle ZIP files
        if file_path.endswith(".zip"):
            logger.debug(f"Processing ZIP file: {file_path}")
            extracted_files = extract_zip(file_path, temp_dir)
            for extracted_file in extracted_files:
                if extracted_file.endswith(".json"):
                    logger.debug(f"Loading documents from JSON file: {extracted_file}")
                    documents.extend(load_documents_from_json(extracted_file, metadata_fields))
                elif extracted_file.endswith(".csv"):
                    logger.debug(f"Loading documents from CSV file: {extracted_file}")
                    documents.extend(load_documents_from_csv(extracted_file, metadata_fields))
                else:
                    logger.warning(f"Unsupported file format skipped: {extracted_file}")
        # Handle JSON files
        elif file_path.endswith(".json"):
            logger.debug(f"Loading documents from JSON file: {file_path}")
            documents = load_documents_from_json(file_path, metadata_fields)
        # Handle CSV files
        elif file_path.endswith(".csv"):
            logger.debug(f"Loading documents from CSV file: {file_path}")
            documents = load_documents_from_csv(file_path, metadata_fields)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

    except Exception as e:
        logger.error(f"Error processing file '{file_path}': {e}")
        raise

    # Cleanup temporary directory
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logger.debug(f"Temporary directory '{temp_dir}' cleaned up.")
        except Exception as e:
            logger.warning(f"Unable to delete temporary directory '{temp_dir}': {e}")

    logger.info(f"Total documents loaded: {len(documents)}")
    return documents