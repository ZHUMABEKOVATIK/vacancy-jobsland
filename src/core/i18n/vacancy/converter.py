import json
import aiofiles

async def read_json_file(path: str) -> dict:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        text = await f.read()
    return json.loads(text)