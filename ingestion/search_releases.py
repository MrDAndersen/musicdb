"""
Module for searching Discogs releases based on specific criteria.
"""

import time
from discogs_client.exceptions import HTTPError
from ingestion.discogs_client import get_discogs_client

def search_releases(query=None, artist=None, title=None, year=None, genre=None, 
                   release_type=None, limit=50, retries=3):
    """
    Search for releases on Discogs matching specified criteria.
    
    Args:
        query (str): General search query string
        artist (str): Artist name to filter by  
        title (str): Release title to filter by
        year (int): Release year to filter by
        genre (str): Genre to filter by
        release_type (str): Format to filter by ('CD', 'LP', etc.)
        limit (int): Maximum number of results to return (default: 50)
        retries (int): Number of retry attempts for API calls
    
    Returns:
        list: List of release data dictionaries matching criteria, or empty list if none found
        
    Example usage:
        # Search for releases by specific artist
        releases = search_releases(artist="The Beatles", limit=10)
        
        # Search with multiple criteria  
        releases = search_releases(
            artist="Radiohead", 
            title="OK Computer",
            year=1997,
            limit=5
        )
    """
    
    d = get_discogs_client()
    
    # Build search parameters dictionary
    search_params = {}
    if query:
        search_params['q'] = query
    if artist:
        search_params['artist'] = artist  
    if title:
        search_params['title'] = title
    if year:
        search_params['year'] = year
    if genre:
        search_params['genre'] = genre
    if format:
        search_params['format'] = format
    
    # Ensure we have at least one search parameter
    if not search_params:
        raise ValueError("At least one search parameter must be provided")
    
    for attempt in range(1, retries + 1):
        try:
            # Perform the search using Discogs client's search method
            results = d.search(**search_params, type='release', per_page=min(limit, 100))
            
            # Collect release data from search results
            releases_data = []
            count = 0
            
            for release in results:
                if count >= limit:
                    break
                    
                try:
                    # Access the title to ensure it's valid (hydrates object)
                    _ = release.title
                    releases_data.append(release.data)
                    count += 1
                except Exception:
                    # Skip invalid releases that can't be hydrated
                    continue
            
            return releases_data
            
        except HTTPError as e:
            # Rate limit or server error → retry  
            if e.status_code in (429, 500, 503, 504):
                sleep_time = attempt * 2
                print(f"Search API rate limited or server error. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
                continue
            
            # Other HTTP errors → don't retry  
            print(f"Search failed with HTTP error {e.status_code}: {str(e)}")
            return []
            
        except Exception as e:
            print(f"Unexpected error during search: {str(e)}")
            return []
    
    print(f"[FAILED] Search after {retries} retries")
    return []

def find_release_by_artist_and_title(artist, title, retries=3):
    """
    Convenience function to find a release by artist and title.
    
    Args:
        artist (str): Artist name
        title (str): Release title  
        retries (int): Number of retry attempts
    
    Returns:
        dict or None: Release data if found, None otherwise
    """
    results = search_releases(artist=artist, title=title, limit=1, retries=retries)
    return results[0] if results else None

def find_release_by_artist_and_year(artist, year, retries=3):
    """
    Convenience function to find releases by artist and year.
    
    Args:
        artist (str): Artist name
        year (int): Release year
        retries (int): Number of retry attempts
    
    Returns:
        list: List of release data matching criteria
    """
    return search_releases(artist=artist, year=year, limit=20, retries=retries)