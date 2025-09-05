import os
from typing import Optional
import uuid
from fastapi import UploadFile
from settings import api_config
import aiofiles


async def save_upload_file(
    file: UploadFile, dest_dir: str = api_config.STATIC_FILES_DIR
) -> Optional[str]:

    if not file:
        return None

    if file.filename:
        filename = f"{uuid.uuid4().hex}_{file.filename}"
        os.makedirs(dest_dir, exist_ok=True)
        dest_path = os.path.join(dest_dir, filename)

        async with aiofiles.open(dest_path, "wb") as out_file:
            while True:
                chunk = await file.read(1024 * 1024)
                if not chunk:
                    break
                await out_file.write(chunk)

        # возвращаем путь, который клиент может открыть: STATIC_URL_PREFIX + filename
        return f"{dest_dir.rstrip('/')}/{filename}"
