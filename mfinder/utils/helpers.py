from typing import Union
import base64
from struct import pack
from pyrogram import raw
from pyrogram.file_id import FileId, FileType, PHOTO_TYPES, DOCUMENT_TYPES
import os
from dotenv import load_dotenv
import requests

load_dotenv()

def get_input_file_from_file_id(
    file_id: str,
    expected_file_type: FileType = None,
) -> Union["raw.types.InputPhoto", "raw.types.InputDocument"]:
    try:
        decoded = FileId.decode(file_id)
    except Exception:
        raise ValueError(
            f'Failed to decode "{file_id}". The value does not represent an existing local file, '
            f"HTTP URL, or valid file id."
        )

    file_type = decoded.file_type

    if expected_file_type is not None and file_type != expected_file_type:
        raise ValueError(
            f'Expected: "{expected_file_type}", got "{file_type}" file_id instead'
        )

    if file_type in (FileType.THUMBNAIL, FileType.CHAT_PHOTO):
        raise ValueError(f"This file_id can only be used for download: {file_id}")

    if file_type in PHOTO_TYPES:
        return raw.types.InputPhoto(
            id=decoded.media_id,
            access_hash=decoded.access_hash,
            file_reference=decoded.file_reference,
        )

    if file_type in DOCUMENT_TYPES:
        return raw.types.InputDocument(
            id=decoded.media_id,
            access_hash=decoded.access_hash,
            file_reference=decoded.file_reference,
        )

    raise ValueError(f"Unknown file id: {file_id}")

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0

    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0

            r += bytes([i])

    return base64.urlsafe_b64encode(r).decode().rstrip("=")

def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")

def unpack_new_file_id(new_file_id):
    """Return file_id, file_ref"""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack(
            "<iiqq",
            int(decoded.file_type),
            decoded.dc_id,
            decoded.media_id,
            decoded.access_hash,
        )
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref

def edit_caption(c_caption):

    org_caption = c_caption

    caption = org_caption.replace(".", " ")
    final_string = " ".join(
        x
        for x in caption.split()
        if not x.startswith(
            (
                "https://",
                "https//",
                "http://",
                "http//",
                "t.me",
                "@",
                "mkv",
                "mp4",
                "avi",
                "mp3",
                "MP3",
            )
        )
    )
    final_string = final_string.replace("_", " ")
    final_string = " ".join(
        x
        for x in final_string.split()
        if not x.startswith(("https://", "http://", "t.me", "@"))
    )
    # final_string = "**" + final_string + "**"
    return final_string

def shorten_url(long_url):
    api_url = "https://krownlinks.com/api"
    api_key = os.getenv("KROWN_API_KEY")
    if not api_key:
        raise Exception("KROWN_API_KEY is not set in .env file")
    params = {
        'url': long_url,
        'api': api_key,
        'format': 'json'
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'success':
            return data['shortenedUrl']
        else:
            raise Exception(f"Error shortening URL: {data['message']}")
    else:
        raise Exception(f"HTTP Error: {response.status_code}")
