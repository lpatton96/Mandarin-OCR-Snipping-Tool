import asyncio
from googletrans import Translator

async def translate_text():
    async with Translator() as translator:
        result = await translator.translate("大家好")
        print(result)  # <Translated src=ko dest=en text=Good evening. pronunciation=Good evening.>

asyncio.run(translate_text())