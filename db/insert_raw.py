import json
from datetime import datetime, timezone

def insert_raw_release(conn, release_id, raw_json):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO discogs.raw_items (discogs_release_id, raw_json, fetched_at)
            VALUES (%s, %s, %s)
            ON CONFLICT (discogs_release_id)
            DO UPDATE SET raw_json = EXCLUDED.raw_json, fetched_at = EXCLUDED.fetched_at;
        """, (release_id, json.dumps(raw_json), datetime.now(timezone.utc)))
