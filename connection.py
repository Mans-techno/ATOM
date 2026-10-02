import asyncpg
from dotenv import load_dotenv
import os 


load_dotenv()


async def connection():
    try:
        conn = await asyncpg.connect(
            user= "ATOM",
            password= os.getenv("DB_PASSWORD"),
            database= "postgres",
            host= "localhost",
            port= 5432
        )
        print("Connection successful")
        return conn
    except Exception as error:
        print(f"Error connecting: {error}")
       

async def create_table():
    conn = await connection()
    if conn is None:
        return
    try:
        await conn.execute('''
            create table if not exists historys(
            history_id serial primary key,
            tg_id varchar,
            message_send text,
            messages_get text
            );
        ''')
        print("Table created successfully")
    except Exception as error:
        print(f"Error creating table: {error}")
    finally:
        await conn.close()
