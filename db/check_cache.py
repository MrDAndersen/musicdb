import psycopg

def needs_refresh(conn, release_id):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT fetched_at < NOW() - INTERVAL '30 days'
            FROM discogs.raw_items
            WHERE discogs_release_id = %s;
        """, (release_id,))
        row = cur.fetchone()

    if row is None:
        return True  # new release

    return row[0]  # True if stale
