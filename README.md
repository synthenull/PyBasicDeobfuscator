## PyBasicDeobfuscator
Basic Python obfuscation unpacker for reversing zlib/base64 wrapped payloads and extracting readable Python source code.

## Overview

PyBasicDeobfuscator is a lightweight Python deobfuscation utility designed for analyzing simple obfuscated Python scripts.

The tool attempts to:
- Detect reversed Base64 payloads
- Decode Base64 / URL-safe Base64 blobs
- Decompress ZLIB-compressed payloads
- Unpack multiple layers automatically
- Recover readable Python source code

## Supported Techniques

The tool currently supports common lightweight obfuscation methods such as:

- Reversed Base64 payloads
- ZLIB-compressed Python code
- Nested/layered wrappers
- Basic exec()-based packers

Example supported patterns:

```python
exec((b'...'))
```

```python
exec(zlib.decompress(base64.b64decode(...)))
```

## Usage

### Run the script

```bash
python PyBasicDeobfuscator.py
```

Then enter the path to the obfuscated `.py` file.

You can also drag & drop the file directly into the console window.

## Output

The unpacked file will be created automatically:

```text
original.py
→
original_deobfuscated.py
```

## Example

Input:

```python
exec((b'...'))
```

Output:

```python
import os

print("Hello World")
```

## Requirements

- Python 3.10+
- Windows (recommended)
