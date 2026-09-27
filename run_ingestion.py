from psycopg import Connection
from psycopg.rows import dict_row

from ingestion.normalize_release import normalize_release
from ingestion.fetch_collection import fetch_collection
from ingestion.fetch_release import fetch_release
import json, time

# ---------------------------
# collection_items helpers
# ---------------------------

def upsert_collection_items(conn: Connection, items):
    cur = conn.cursor()
    if items:
        print(f"First item data keys: {list(items[0].data.keys()) if hasattr(items[0], "data") else "No .data attribute"}")
    cur.executemany(
        """
        INSERT INTO discogs.collection_items (
            instance_id, release_id, folder_id, date_added, rating, notes
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (instance_id) DO UPDATE SET
            release_id = EXCLUDED.release_id,
            folder_id = EXCLUDED.folder_id,
            date_added = EXCLUDED.date_added,
            rating = EXCLUDED.rating,
            notes = EXCLUDED.notes;
        """,
        [
            (
                item.data["instance_id"],   # collection instance id
                item.data["id"],            # release id
                item.data["folder_id"],     # folder id
                item.data["date_added"],    # date added
                item.rating,                 # rating
                item.notes.__str__() if item.notes else None                 # notes
            )
            for item in items
        ]
    )


def prune_removed_collection_items(conn: Connection, current_instance_ids):
    cur = conn.cursor()

    if not current_instance_ids:
        # If the list is empty, delete everything
        cur.execute("DELETE FROM discogs.collection_items;")
        return

    placeholders = ",".join(["%s"] * len(current_instance_ids))

    cur.execute(
        f"""
        DELETE FROM discogs.collection_items
        WHERE instance_id NOT IN ({placeholders});
        """,
        tuple(current_instance_ids)
    )

# ---------------------------
# vinyl_items archive
# ---------------------------

def archive_removed_vinyl_items(conn: Connection, current_release_ids):
    cur = conn.cursor(row_factory=dict_row)

    placeholders = ",".join(["%s"] * len(current_release_ids))
    cur.execute(
        f"""
        SELECT *
        FROM vinyl.vinyl_items
        WHERE discogs_release_id IS NOT NULL
          AND discogs_release_id NOT IN ({placeholders});
        """,
        tuple(current_release_ids)
    )
    removed = cur.fetchall()
    if not removed:
        return

    archive_rows = [
        (
            row["id"], row["catalog_number"], row["title"], row["artist"],
            row["year"], row["label"], row["label_code"], row["catalog_code"],
            row["pressing_type"], row["mastering_chain"], row["mastering_engineer"],
            row["pressing_plant"], row["format"], row["discogs_release_id"],
            row["discogs_url"], row["cover_image_url"], row["thumbnail_url"],
            row["condition_media"], row["condition_sleeve"], row["completeness_score"],
            row["notes"], row["acquisition_story"], row["created_at"], row["updated_at"],
            row["deadwax_side_a"], row["deadwax_side_b"], row["deadwax_other_sides"],
            row["acquisition_date"]
        )
        for row in removed
    ]

    cur.executemany(
        """
        INSERT INTO vinyl.vinyl_items_archive (
            id, catalog_number, title, artist, year, label, label_code,
            catalog_code, pressing_type, mastering_chain, mastering_engineer,
            pressing_plant, format, discogs_release_id, discogs_url,
            cover_image_url, thumbnail_url, condition_media, condition_sleeve,
            completeness_score, notes, acquisition_story, created_at,
            updated_at, deadwax_side_a, deadwax_side_b, deadwax_other_sides,
            acquisition_date, archived_at
        )
        VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW()
        )
        ON CONFLICT (id) DO NOTHING;
        """,
        archive_rows
    )

    cur.execute(
        f"""
        DELETE FROM vinyl.vinyl_items
        WHERE discogs_release_id IS NOT NULL
          AND discogs_release_id NOT IN ({placeholders});
        """,
        tuple(current_release_ids)
    )


# ---------------------------
# raw_items helpers
# ---------------------------

def get_existing_raw_release_ids(conn: Connection):
    cur = conn.cursor()
    cur.execute("SELECT discogs_release_id FROM discogs.raw_items;")
    return {row[0] for row in cur.fetchall()}


def upsert_raw_item(conn: Connection, release_id, raw_json):
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO discogs.raw_items (discogs_release_id, raw_json, fetched_at)
        VALUES (%s, %s, NOW())
        ON CONFLICT (discogs_release_id) DO UPDATE SET
            raw_json = EXCLUDED.raw_json,
            fetched_at = EXCLUDED.fetched_at;
        """,
        (release_id, raw_json)
    )


# ---------------------------
# curated tables helpers
# ---------------------------

def insert_curated_tables(conn: Connection, normalized, release_id):
    cur = conn.cursor()

    # releases
    rel = normalized["releases"]
    cur.execute(
        """
        INSERT INTO discogs.releases (release_id, title, year, country, notes, master_id, data_hash)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (release_id) DO UPDATE SET
            title = EXCLUDED.title,
            year = EXCLUDED.year,
            country = EXCLUDED.country,
            notes = EXCLUDED.notes,
            master_id = EXCLUDED.master_id,
            data_hash = EXCLUDED.data_hash;
        """,
        (
            rel["release_id"], rel["title"], rel["year"], rel["country"],
            rel["notes"], rel["master_id"], rel["data_hash"]
        )
    )

    # artists
    cur.executemany(
        """
        INSERT INTO discogs.artists (artist_id, name, anv)
        VALUES (%s, %s, %s)
        ON CONFLICT (artist_id) DO UPDATE SET
            name = EXCLUDED.name,
            anv = EXCLUDED.anv;
        """,
        [
            (a["artist_id"], a["name"], a["anv"])
            for a in normalized["artists"]
        ]
    )

    # release_artists
    cur.executemany(
        """
        INSERT INTO discogs.release_artists (release_id, artist_id, role, join_string)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """,
        [
            (ra["release_id"], ra["artist_id"], ra["role"] if ra["role"] else "artist", ra["join_string"])
            for ra in normalized["release_artists"]
        ]
    )

    # labels
    cur.executemany(
        """
        INSERT INTO discogs.labels (label_id, name)
        VALUES (%s, %s)
        ON CONFLICT (label_id) DO UPDATE SET
            name = EXCLUDED.name;
        """,
        [
            (l["label_id"], l["name"])
            for l in normalized["labels"]
        ]
    )

    # release_labels
    cur.executemany(
        """
        INSERT INTO discogs.release_labels (release_id, label_id, catno, entity_type)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """,
        [
            (rl["release_id"], rl["label_id"], rl["catno"], rl["entity_type"])
            for rl in normalized["release_labels"]
        ]
    )

    # formats
    # cur.executemany(
    #     """
    #     INSERT INTO discogs.formats (name, qty, text, descriptions)
    #     VALUES (%s, %s, %s, %s);
    #     """,
    #     [
    #         (f["name"], f["qty"], f["text"], f["descriptions"])
    #         for f in normalized["formats"]
    #     ]
    # )


    cur = conn.cursor()
    
    for fmt in normalized["formats"]:
        
        name = fmt.get("name")
        qty = fmt.get("qty")
        text = fmt.get("text")
        descriptions = fmt.get("descriptions")

        # 1. Insert or fetch format_id
        cur.execute(
            """
            INSERT INTO discogs.formats (name, qty, text, descriptions)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (name, qty, text, descriptions)
            DO NOTHING
            RETURNING format_id;
            """,
            (name, qty, text, descriptions)
        )

        row = cur.fetchone()

        if row:
            format_id = row[0]
        else:
            # Fetch existing
            cur.execute(
                """
                SELECT format_id
                FROM discogs.formats
                WHERE name = %s AND qty = %s AND text = %s AND descriptions = %s;
                """,
                (name, qty, text, descriptions)
            )
            format_id = cur.fetchone()[0]

        # 2. Insert into release_formats
        cur.execute(
            """
            INSERT INTO discogs.release_formats (release_id, format_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (release_id, format_id)
        )



    # identifiers
    cur.executemany(
        """
        INSERT INTO discogs.identifiers (release_id, type, value, description)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """,
        [
            (i["release_id"], i["type"], i["value"], i["description"])
            for i in normalized["identifiers"]
        ]
    )

    # companies
    cur.executemany(
        """
        INSERT INTO discogs.companies (company_id, name, entity_type, entity_type_name)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (company_id) DO UPDATE SET
            name = EXCLUDED.name,
            entity_type = EXCLUDED.entity_type,
            entity_type_name = EXCLUDED.entity_type_name;
        """,
        [
            (c["company_id"], c["name"], c["entity_type"], c["entity_type_name"])
            for c in normalized["companies"]
        ]
    )

    # release_companies
    cur.executemany(
        """
        INSERT INTO discogs.release_companies (release_id, company_id, role)
        VALUES (%s, %s, %s)
        ON CONFLICT DO NOTHING;
        """,
        [
            (rc["release_id"], rc["company_id"], rc["role"])
            for rc in normalized["release_companies"]
        ]
    )

    # tracks
    cur.executemany(
        """
        INSERT INTO discogs.tracks (release_id, position, title, duration)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT DO NOTHING;
        """,
        [
            (t["release_id"], t["position"], t["title"], t["duration"])
            for t in normalized["tracks"]
        ]
    )


# ---------------------------
# final ingestion runner
# ---------------------------

def run_ingestion(conn: Connection, discogs_client):
    # Phase 1: fetch collection (for release_ids)
    print("Phase 1: Fetching collection from Discogs...")
    collection = fetch_collection()
    current_release_ids = {item.data["id"] for item in collection}
    current_instance_ids = {item.data["instance_id"] for item in collection}

    # # Phase 2: sync raw_items
    # print("Phase 2: Syncing raw_items...")
    # existing_raw = get_existing_raw_release_ids(conn)
    # missing = current_release_ids - existing_raw

    # for release_id in missing:
    #     raw_json = fetch_release(release_id)
    #     upsert_raw_item(conn, release_id, json.dumps(raw_json))
    #     time.sleep(1)  # be nice to the API
    # conn.commit()


    # Phase 3: normalize curated tables (ensures discogs.releases exists for FK)
    print("Phase 3: Normalizing curated tables...")
    # cur = conn.cursor()
    # cur.execute("SELECT discogs_release_id, raw_json FROM discogs.raw_items;")
    # for release_id, raw_json in cur.fetchall():
    #     normalized = normalize_release( raw_json)
    #     insert_curated_tables(conn, normalized, release_id)
    # conn.commit()

    # Phase 4: upsert collection_items (FK-safe now)
    print("Phase 4: Upserting collection_items...")
    upsert_collection_items(conn, collection)
    conn.commit()

    # Phase 5: prune removed collection_items
    print("Phase 5: Pruning removed collection_items...")
    prune_removed_collection_items(conn, current_instance_ids)
    conn.commit()

    # Phase 6: archive removed vinyl_items
    print("Phase 6: Archiving removed vinyl_items...")
    archive_removed_vinyl_items(conn, current_release_ids)
    conn.commit()

    print("Ingestion complete.")

if __name__ == "__main__":
    from db.connection import get_connection
    from ingestion.discogs_client import get_discogs_client

    conn = get_connection()
    discogs_client = get_discogs_client()

    run_ingestion(conn, discogs_client)
