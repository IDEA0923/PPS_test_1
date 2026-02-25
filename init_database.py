import json
import os
import asyncpg
from datetime import datetime

async def get_database_info(request: str) -> str:
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    try:

        rows = await conn.fetch(request)
        if not rows:
            return ""
        

        if len(rows) == 1 and len(rows[0]) == 1:
            return f"{rows[0][0]}"
            

        res_list = []
        for r in rows:
            res_list.append(" | ".join(str(v) for v in r))
        return "\n".join(res_list)
    except Exception as e:
        return f"{e}"
    finally:
        await conn.close()

async def init_db_and_load_json():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
    

    await conn.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            creator_id TEXT,
            video_created_at TIMESTAMP,
            views_count INT,
            likes_count INT,
            comments_count INT,
            reports_count INT
        );
        CREATE TABLE IF NOT EXISTS video_snapshots (
            id SERIAL PRIMARY KEY,
            video_id TEXT REFERENCES videos(id),
            timestamp TIMESTAMP,
            views_count INT,
            likes_count INT,
            comments_count INT,
            reports_count INT,
            delta_views_count INT,
            delta_likes_count INT,
            delta_comments_count INT,
            delta_reports_count INT
        );
    ''')


    if await conn.fetchval("SELECT COUNT(*) FROM videos") == 0:
        print("Загружаем данные из JSON...")
        with open('videos.json', 'r') as f:
            data = json.load(f)
            for v in data['videos']:

                video_date = datetime.fromisoformat(v['video_created_at'].replace('Z', '+00:00')).replace(tzinfo=None)

                await conn.execute('''
                    INSERT INTO videos (id, creator_id, video_created_at, views_count, likes_count, comments_count, reports_count)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                ''', v['id'], v['creator_id'], video_date, v['views_count'], v['likes_count'], v['comments_count'], v['reports_count'])
                
                for s in v.get('snapshots', []):

                    snapshot_date = datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).replace(tzinfo=None)

                    await conn.execute('''
                        INSERT INTO video_snapshots (video_id, timestamp, views_count, likes_count, comments_count, reports_count, 
                        delta_views_count, delta_likes_count, delta_comments_count, delta_reports_count)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                    ''', v['id'], snapshot_date, s['views_count'], s['likes_count'], s['comments_count'], s['reports_count'],
                    s['delta_views_count'], s['delta_likes_count'], s['delta_comments_count'], s['delta_reports_count'])
        print("Данные успешно загружены!")
    
    await conn.close()