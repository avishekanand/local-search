import unittest
import os
import sys

# Add the project root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.utils.compression_utils import compress_folder

compress_folder("/Users/avishekanand/Projects/search-engine/index", "/Users/avishekanand/Projects/search-engine/index/compressed", method="zstd")