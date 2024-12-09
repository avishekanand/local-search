import os
import json
import gzip
import snappy
import zstandard as zstd


def compress_file_snappy(input_file: str, output_file: str):
    """
    Compress a file using Snappy.
    """
    with open(input_file, 'r') as f:
        data = f.read()
    compressed_data = snappy.compress(data)
    with open(output_file, 'wb') as f:
        f.write(compressed_data)


def decompress_file_snappy(input_file: str) -> str:
    """
    Decompress a Snappy-compressed file and return its content as a string.
    """
    with open(input_file, 'rb') as f:
        compressed_data = f.read()
    return snappy.uncompress(compressed_data).decode()


def compress_file_gzip(input_file: str, output_file: str):
    """
    Compress a file using Gzip.
    """
    with open(input_file, 'r') as f:
        data = f.read()
    with gzip.open(output_file, 'wt') as f:
        f.write(data)


def decompress_file_gzip(input_file: str) -> str:
    """
    Decompress a Gzip-compressed file and return its content as a string.
    """
    with gzip.open(input_file, 'rt') as f:
        return f.read()


def compress_file_zstd(input_file: str, output_file: str, level: int = 3):
    """
    Compress a file using Zstandard.
    """
    with open(input_file, 'r') as f:
        data = f.read().encode()
    cctx = zstd.ZstdCompressor(level=level)
    compressed_data = cctx.compress(data)
    with open(output_file, 'wb') as f:
        f.write(compressed_data)


def     decompress_file_zstd(input_file: str) -> str:
    """
    Decompress a Zstandard-compressed file and return its content as a string.
    """
    with open(input_file, 'rb') as f:
        compressed_data = f.read()
    dctx = zstd.ZstdDecompressor()
    return dctx.decompress(compressed_data).decode()


def compress_folder(input_folder: str, output_folder: str, method: str = 'snappy'):
    """
    Compress all valid JSON files in a folder using the specified method.
    Skips non-JSON files, nested directories, and invalid paths.

    Supported methods: 'snappy', 'gzip', 'zstd'.
    """
    if not os.path.exists(input_folder):
        raise FileNotFoundError(f"Input folder '{input_folder}' does not exist.")
    if not os.path.isdir(input_folder):
        raise NotADirectoryError(f"Input path '{input_folder}' is not a directory.")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file_name in os.listdir(input_folder):
        input_path = os.path.join(input_folder, file_name)

        # Skip directories and non-JSON files
        if not os.path.isfile(input_path):
            print(f"Skipping non-file: {input_path}")
            continue
        if not file_name.endswith(".json"):
            print(f"Skipping non-JSON file: {file_name}")
            continue

        output_path = os.path.join(output_folder, f"{file_name}.{method}")

        try:
            if method == 'snappy':
                compress_file_snappy(input_path, output_path)
            elif method == 'gzip':
                compress_file_gzip(input_path, output_path)
            elif method == 'zstd':
                compress_file_zstd(input_path, output_path)
            else:
                raise ValueError(f"Unsupported compression method: {method}")

            print(f"Compressed {file_name} to {output_path}")

        except Exception as e:
            print(f"Error compressing {file_name}: {e}")


def decompress_file(input_file: str, method: str = 'snappy') -> str:
    """
    Decompress a file using the specified method.
    Supported methods: 'snappy', 'gzip', 'zstd'.
    """
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file '{input_file}' does not exist.")
    if not os.path.isfile(input_file):
        raise NotAFileError(f"Input path '{input_file}' is not a file.")

    try:
        if method == 'snappy':
            return decompress_file_snappy(input_file)
        elif method == 'gzip':
            return decompress_file_gzip(input_file)
        elif method == 'zstd':
            return decompress_file_zstd(input_file)
        else:
            raise ValueError(f"Unsupported decompression method: {method}")
    except Exception as e:
        raise RuntimeError(f"Error decompressing file '{input_file}': {e}")