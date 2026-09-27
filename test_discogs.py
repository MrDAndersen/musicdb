from ingestion.fetch_release import fetch_release

def main():
    release_id = "11853440"  # any known release ID
    data = fetch_release(release_id)
    print("Fetched release title:", data.get("title"))

if __name__ == "__main__":
    main()
