from aiogram import Dispatcher , Bot , html  
from aiogram.types import Message

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

import asyncio , logging , sys 
import asyncpg

from openai import OpenAI , AsyncOpenAI

from config import TOKEN , API_from_open_router , base_prompt , model_for_use

dp = Dispatcher()
import time
time.sleep(5)
import init_database
###################
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_from_open_router,
)

async def get_SQL_request(text: str)-> str:    
    response = await client.chat.completions.create(
        model=model_for_use,
        messages=[
            {"role": "system", "content": base_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0 # Небольшая температура помогает модели быть стабильнее
    )
    sql = response.choices[0].message.content.strip()
    return sql.replace("```sql", "").replace("```", "").strip()

@dp.message()
async def all_other_messages(mess : Message):
    SQL_request =await get_SQL_request(mess.text)
    answer = await init_database.get_database_info(SQL_request)
    print(f"request: {mess.text} ")
    print(f"request: {mess.text} \n SQL : {SQL_request} \n answer : {answer}")
    await mess.reply(answer)

async def main()-> None:
    await init_database.init_db_and_load_json()
    bot = Bot(token=TOKEN , default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ =="__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

