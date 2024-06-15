from typing import Union

import asyncpg
from asyncpg import Connection
from asyncpg.pool import Pool
from data import config


class Database:

    def __init__(self):
        self.pool: Union[Pool, None] = None

    async def create(self):
        self.pool = await asyncpg.create_pool(
            user=config.DB_USER,
            password=config.DB_PASS,
            host=config.DB_HOST,
            database=config.DB_NAME
        )

    async def execute(self, command, *args,
                      fetch: bool = False,
                      fetchval: bool = False,
                      fetchrow: bool = False,
                      execute: bool = False
                      ):
        async with self.pool.acquire() as connection:
            connection: Connection
            async with connection.transaction():
                if fetch:

                    result = await connection.fetch(command, *args)
                elif fetchval:
                    result = await connection.fetchval(command, *args)
                elif fetchrow:
                    result = await connection.fetchrow(command, *args)
                elif execute:
                    result = await connection.execute(command, *args)
            return result

    async def create_data_history(self):
        sql = """
        CREATE TABLE IF NOT EXISTS history (
        id SERIAL PRIMARY KEY,
        data_time VARCHAR(30) NULL,
        data_open VARCHAR(30) NULL,
        data_high VARCHAR(30) NULL,
        data_low VARCHAR(30) NULL,
        data_close VARCHAR(30) NULL,
        data_volume VARCHAR(30) NULL,
        data_ema20 VARCHAR(30) NULL,
        data_ema50 VARCHAR(30) NULL,
        data_ema100 VARCHAR(30) NULL,
        data_ema200 VARCHAR(30) NULL,
        bollinger_high VARCHAR(30) NULL,
        bollinger_low VARCHAR(30) NULL,
        atr14 VARCHAR(30) NULL,
        adx14 VARCHAR(30) NULL,
        rsi7 VARCHAR(30) NULL,
        rsi50 VARCHAR(30) NULL,
        stochastic VARCHAR(60) NULL,
        ichimoku VARCHAR(60) NULL
        );
        """
        await self.execute(sql, execute=True)

    async def add_history(self, telegram_id):
        sql = "INSERT INTO history (telegram_id) VALUES($1) returning *"
        return await self.execute(sql, telegram_id, fetchrow=True)

    # async def select_history_one(self, id):
    #     sql = "SELECT * FROM history WHERE id=$1"
    #     return await self.execute(sql, id, fetchrow=True)

    async def select_history_all(self):
        sql = "SELECT * FROM history"
        return await self.execute(sql, fetch=True)

    #
    # async def update_student_language(self, language, telegram_id):
    #     sql = "UPDATE history SET language=$1 WHERE telegram_id=$2"
    #     return await self.execute(sql, language, telegram_id, execute=True)
    #
    #
    # async def update_student_pay_message(self, pay_message_id, telegram_id):
    #     sql = "UPDATE history SET pay_message_id=$1 WHERE telegram_id=$2"
    #     return await self.execute(sql, pay_message_id, telegram_id, execute=True)
    #
    #
    # async def delete_lifetime(self, user_id):
    #     sql = "DELETE FROM lifetime WHERE user_id=$1"
    #     return await self.execute(sql, user_id, fetch=True)
