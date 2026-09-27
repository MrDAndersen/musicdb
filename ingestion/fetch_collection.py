from ingestion.discogs_client import get_discogs_client

def fetch_collection():
    d = get_discogs_client()
    me = d.identity()

    folder = me.collection_folders[0]
    releases = folder.releases  # <-- THIS is the PaginatedList

    total_pages = releases.pages
    print(f"Collection has {total_pages} pages.")

    items = []
    for page in range(1, total_pages + 1):
        print(f"Fetching page {page}/{total_pages}…")
        page_items = releases.page(page)  # <-- safe now
        items.extend(page_items)

    return items
