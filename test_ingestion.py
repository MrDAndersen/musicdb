from db.connection import get_connection
from ingestion.fetch_release import fetch_release
from db.insert_raw import insert_raw_release

def main():
    release_id = 6383425
    raw = fetch_release(release_id)
    conn = get_connection()
    insert_raw_release(conn, release_id, raw)
    conn.commit()
    conn.close()

    print("Inserted release:", release_id)

if __name__ == "__main__":
    main()
