# developed by akgvnx - github.com/akgvnx

from __future__ import annotations
import ast
import base64
import hashlib
import os
import re
import sys
import zlib
from pathlib import Path

def zlib_marshal_try_layer(text: str) -> bytes | None:
    m = re.search(r"exec\(\s*\(?_?\)?\s*\(b'(.+?)'\)\)", text, re.S)
    blob: bytes | None = None
    if m:
        blob = ast.literal_eval("b'" + m.group(1) + "'")
    else:
        m = re.search(r"b'([A-Za-z0-9+/=\r\n\t ]+)'", text, re.S)
        if m:
            blob = ast.literal_eval("b'" + m.group(1) + "'")
        else:
            m = re.search(r"([A-Za-z0-9+/]{200,}={0,2})", text)
            if m:
                blob = m.group(1).encode("ascii")
            else:
                return None

    rev = re.sub(rb"[\r\n\t ]+", b"", blob)[::-1]
    rev += b"=" * (-len(rev) % 4)

    raw: bytes | None = None
    for dec in (base64.b64decode, base64.urlsafe_b64decode):
        try:
            raw = dec(rev)
            break
        except Exception:
            raw = None
    if raw is None:
        return None

    try:
        return zlib.decompress(raw)
    except Exception:
        return raw

def looks_like_valid_code(content: bytes) -> bool:
    try:
        text = content.decode("utf-8", "ignore")
        indicators = ["import ", "def ", "class ", "if ", "for ", "while ", "print(", "return "]
        score = sum(1 for indicator in indicators if indicator in text)
        printable_ratio = sum(
            1 for c in text if 32 <= ord(c) < 127 or c in "\n\r\t"
        ) / max(len(text), 1)
        return score >= 2 and printable_ratio > 0.7
    except Exception:
        return False

def deobfuscate_text(content: str, *, max_layers: int = 100) -> str:
    cur = content
    seen_hashes: set[str] = set()
    best: bytes | None = None
    last: bytes | None = None

    for _layer in range(1, max_layers + 1):
        nxt = zlib_marshal_try_layer(cur)
        if not nxt:
            break

        last = nxt
        h = hashlib.md5(nxt).hexdigest()
        if h in seen_hashes:
            break
        seen_hashes.add(h)

        if looks_like_valid_code(nxt):
            best = nxt

        try:
            cur = nxt.decode("utf-8", "ignore")
        except Exception:
            break

    out_bytes = best or last
    if not out_bytes:
        raise RuntimeError(" [-] The ZLIB/Marshal layer could not be found or parsed.")

    return out_bytes.decode("utf-8", "replace")

def normalize_path(raw: str) -> Path:
    return Path(raw.strip().strip('"').strip("'")).expanduser().resolve()

def prompt_py_path(message: str = " [>] Enter the path to the obfuscated .py file: ") -> Path:
    while True:
        raw = input(message).strip()
        if not raw:
            print(" [!] The file location can't be empty.")
            continue
        path = normalize_path(raw)
        if not path.exists():
            print(f" [-] File not found: {path}")
            continue
        if path.suffix.lower() != ".py":
            print(" [!] Only .py files are supported.")
            continue
        return path

def deobfuscate_file(
    input_path: Path,
    output_path: Path | None = None,
    *,
    max_layers: int = 100,
) -> Path:
    if not input_path.exists():
        raise FileNotFoundError(f"[-] File not found: {input_path}")
    if input_path.suffix.lower() != ".py":
        raise ValueError(" [!] The input file must be a .py file.")

    text = input_path.read_text(encoding="utf-8", errors="ignore")
    result = deobfuscate_text(text, max_layers=max_layers)

    if output_path is None:
        output_path = input_path.with_name(f"{input_path.stem}_deobfuscated.py")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "# Unpacked with https://github.com/akgvnx/PyBasicDeobfuscator\n"
        f"# Python Version: {'.'.join(map(str, sys.version_info[:3]))}\n"
    )
    output_path.write_text(header + result, encoding="utf-8", errors="replace")
    return output_path

def pause_before_exit() -> None:
    try:
        input("\n [+] Press enter for exit.")
    except (EOFError, KeyboardInterrupt):
        pass

def main() -> int:
    os.system("cls")
    os.system("title ")
    os.system("color b")
    print("\n [^] Welcome to Akgvnx Basic Unpacker!\n")
    print(" [>] Enter the path to the obfuscated .py file.")
    print(" [>] (You can drag and drop the file into this window.)\n")
    input_path = prompt_py_path(" [>] Path: ")

    code = 0
    try:
        out = deobfuscate_file(input_path)
        os.system("cls")
        os.system("color a")
        print(f"\n [+] Successful.\n [+] Output: {out}")
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        os.system("cls")
        os.system("color b")
        print(f"\n [-] Error: {exc}", file=sys.stderr)
        code = 1

    pause_before_exit()
    return code
    
if __name__ == "__main__":
    raise SystemExit(main())
