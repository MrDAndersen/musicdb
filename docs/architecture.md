# Solution architecture 

## Overview
Two or three sentences on how the system is shaped, pointing to project_requirements.md for the "what" instead of restating it.
Add a "last reviewed" date.

## System Context
What sits outside the system: the Discogs API, PostgreSQL, the storage account for images if you choose it, and the user (CLI, scripts, or a UI).
A simple diagram works well here. Mermaid renders in GitHub, so you can keep it in the file.

## Components 
One short entry per module: what it does, what it depends on, what it must not do. For you that's roughly the Discogs client wrapper, fetch_release, search_releases, normalization, the database layer, and the ingestion runner.
Include the seam between your code and third-party libraries, since that's where the HTTPError and Client.search surprises came from.

## Data flows
One walkthrough for each sync mode: Discogs collection to database, and database to Discogs (search, confirm, add).
List the steps in order and note where the user is asked to confirm. Reference the FR IDs each flow satisfies.
Add the image-identification flow here once you've settled where images enter.

## Data Model
Raw versus normalized tables, how they relate, and the key columns (Discogs IDs, collection instance IDs).
How idempotency is handled (upserts, unique keys), how removed items are flagged, and where images and their metadata live.
A schema diagram or table list is enough. Link the SQL files if they exist.

## External interfaces
Discogs API: which endpoints you use, authentication, the rate limit, the retry policy (429/500/503/504, three attempts), and error handling.
Note any behaviors you verified from source, such as how Client.search handles keyword arguments.

## Configuration and secrets 
Which settings come from .env, what each one means, and a rule that secrets never go in the repo.
Environment: the venv location and how the database runs (Docker, for example).

## Error handling and logging
Which errors are retried, which are skipped, and which abort a run.
What gets logged and where. This section will come up when you decide about the silent except blocks.

## Testing approach 
Test layout, the mocking policy (never the live API), and which layers get unit versus integration tests.
Keep it short and point to the Testing section of the requirements file.

## Key Decisions
A short log: the decision, the reason, the alternatives you rejected, and the date. Examples: invalid IDs raise ValueError, or the image storage choice once you make it.
List open decisions separately, with the trade-offs you already know (blobs against a storage account).

## Known gaps ans technical debt
Things the architecture doesn't handle yet, like the commented-out Phase 2 and the TODO on format IDs, so a reviewer doesn't mistake them for oversights
