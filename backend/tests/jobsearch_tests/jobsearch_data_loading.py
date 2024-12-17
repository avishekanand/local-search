import unittest
import os
import sys

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from backend.app.services.data_loader import load_documents

class TestDataLoader(unittest.TestCase):
    def setUp(self):
        """
        Set up paths to test files.
        """
        self.zip_file_path = "/Users/avishekanand/Projects/search-engine/data/documents/job_postings.csv.zip"
        self.metadata_file_path = "/Users/avishekanand/Projects/search-engine/data/documents/metadata.csv"
        self.temp_dir = "./temp_test"

    def test_load_documents_from_zip(self):
        """
        Test loading documents from a ZIP file containing a CSV and show progress.
        """
        # Ensure the test files exist
        self.assertTrue(os.path.exists(self.zip_file_path), "ZIP file not found")
        self.assertTrue(os.path.exists(self.metadata_file_path), "Metadata file not found")

        # Load documents
        documents = load_documents(self.zip_file_path, self.metadata_file_path, temp_dir=self.temp_dir)

        # Progress tracking
        total_docs = len(documents)
        print(f"Total documents loaded: {total_docs}")

        for i, doc in enumerate(documents, 1):
            if i % 10000 == 0 or i == total_docs:
                print(f"Progress: {i}/{total_docs} documents ingested")

        # Display top 10 documents
        print("\nTop 10 documents:")
        for idx, doc in enumerate(documents[:10], 1):
            print(f"\nDocument {idx}:")
            for key, value in vars(doc).items():
                print(f"  {key}: {value}")

        # Ensure documents are loaded
        self.assertGreater(len(documents), 0, "No documents loaded")

if __name__ == "__main__":
    unittest.main()