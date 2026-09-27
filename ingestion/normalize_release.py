# ingestion/normalize_release.py

def normalize_release(raw):
    """
    Orchestrates extraction of all curated tables from a Discogs release JSON.
    Returns a dict of table_name -> list_of_rows.
    """

    release_id = raw["id"]

    return {
        "releases": extract_release(raw),
        "artists": extract_artists(raw),
        "release_artists": extract_release_artists(raw),
        "labels": extract_labels(raw),
        "release_labels": extract_release_labels(raw),
        "formats": extract_formats(raw),
        "release_formats": extract_release_formats(raw),
        "identifiers": extract_identifiers(raw),
        "companies": extract_companies(raw),
        "release_companies": extract_release_companies(raw),
        "tracks": extract_tracks(raw),
    }


# ------------------------------------------------------------
# Release
# ------------------------------------------------------------

def extract_release(raw):
    
    return {
        "release_id": raw["id"],
        "title": raw.get("title"),
        "year": raw.get("year"),
        "country": raw.get("country"),
        "notes": raw.get("notes"),
        "master_id": raw.get("master_id"),
        "data_hash": None  # optional: fill with hash(raw_json)
    }


# ------------------------------------------------------------
# Artists
# ------------------------------------------------------------

def extract_artists(raw):
    artists = raw.get("artists", [])
    rows = []

    for a in artists:
        rows.append({
            "artist_id": a["id"],
            "name": a.get("name"),
            "anv": a.get("anv")
        })

    return rows


def extract_release_artists(raw):
    release_id = raw["id"]
    artists = raw.get("artists", [])
    rows = []

    for a in artists:
        rows.append({
            "release_id": release_id,
            "artist_id": a["id"],
            "role": None,
            "join_string": a.get("join")
        })

    return rows


# ------------------------------------------------------------
# Labels
# ------------------------------------------------------------

def extract_labels(raw):
    labels = raw.get("labels", [])
    rows = []

    for l in labels:
        rows.append({
            "label_id": l["id"],
            "name": l.get("name")
        })

    return rows


def extract_release_labels(raw):
    release_id = raw["id"]
    labels = raw.get("labels", [])
    rows = []

    for l in labels:
        rows.append({
            "release_id": release_id,
            "label_id": l["id"],
            "catno": l.get("catno"),
            "entity_type": l.get("entity_type")
        })

    return rows


# ------------------------------------------------------------
# Formats
# ------------------------------------------------------------

def extract_formats(raw):
    formats = raw.get("formats", [])
    rows = []

    for f in formats:
        rows.append({
            "name": f.get("name"),
            "qty": f.get("qty"),
            "text": f.get("text"),
            "descriptions": f.get("descriptions", [])
        })

    return rows


def extract_release_formats(raw):
    release_id = raw["id"]
    formats = raw.get("formats", [])
    rows = []

    # formats do not have IDs in Discogs JSON — they are local to the release
    # You will insert formats first, get their format_id, then map them here.
    # For now, return placeholder rows.
    for idx, _ in enumerate(formats):
        rows.append({
            "release_id": release_id,
            "format_id": None  # filled in by ETL after insert
        })

    return rows


# ------------------------------------------------------------
# Identifiers (runouts, barcodes, matrix codes)
# ------------------------------------------------------------

def extract_identifiers(raw):
    release_id = raw["id"]
    identifiers = raw.get("identifiers", [])
    rows = []

    for ident in identifiers:
        rows.append({
            "release_id": release_id,
            "type": ident.get("type"),
            "value": ident.get("value"),
            "description": ident.get("description")
        })

    return rows


# ------------------------------------------------------------
# Companies
# ------------------------------------------------------------

def extract_companies(raw):
    companies = raw.get("companies", [])
    rows = []

    for c in companies:
        rows.append({
            "company_id": c["id"],
            "name": c.get("name"),
            "entity_type": c.get("entity_type"),
            "entity_type_name": c.get("entity_type_name")
        })

    return rows


def extract_release_companies(raw):
    release_id = raw["id"]
    companies = raw.get("companies", [])
    rows = []

    for c in companies:
        rows.append({
            "release_id": release_id,
            "company_id": c["id"],
            "role": c.get("entity_type_name")
        })

    return rows


# ------------------------------------------------------------
# Tracks
# ------------------------------------------------------------

def extract_tracks(raw):
    release_id = raw["id"]
    tracks = raw.get("tracklist", [])
    rows = []

    for t in tracks:
        rows.append({
            "release_id": release_id,
            "position": t.get("position"),
            "title": t.get("title"),
            "duration": t.get("duration")
        })

    return rows
