from connection import connection


async def save_message(tg_id, message_send, messages_get):
    conn = await connection()
    if conn is None:
        return
    try:
        await conn.execute('''
            insert into historys(tg_id, message_send, messages_get)
            values($1, $2, $3);
        ''', str(tg_id), message_send, messages_get)
    except Exception as error:
        print(f"Error saving message: {error}")
    finally:
        await conn.close()



async def get_history(tg_id, limit=20):
    conn = await connection()
    if conn is None:
        return []
    try:
        rows = await conn.fetch('''
            select message_send, messages_get from (
                select history_id, message_send, messages_get from historys
                where tg_id = $1
                order by history_id desc
                limit $2
            ) as last_messages
            order by history_id;
        ''', str(tg_id), limit)
    except Exception as error:
        print(f"Error getting history: {error}")
        return []
    finally:
        await conn.close()

    history = []
    for row in rows:
        history.append({"role": "user", "content": row["message_send"]})
        history.append({"role": "assistant", "content": row["messages_get"]})
    return history



async def clear_history(tg_id):
    conn = await connection()
    if conn is None:
        return
    try:
        await conn.execute('''
            delete from historys where tg_id = $1;
        ''', str(tg_id))
    except Exception as error:
        print(f"Error clearing history: {error}")
    finally:
        await conn.close()
