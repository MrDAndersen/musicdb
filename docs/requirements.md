# Music database project requirements

## Purpose and scope
The purpose of this project is to streamline management of a music collection. The project enables sync between music collection data in a PostgreSQL database and the user's Discogs collection. This means the system will be able to retrieve data on an album from the database and search the Discogs database for this album to get additional metadata. If the album is not in the user's collection the system will ask if the user wants to add it to the collection. The system can also retrieve the user's collection from Discogs and add the entries that are not already in the database to the database and flag entries that are in the database but not in the collection for the user's review. The user will be able to supply images of the labels, jackets and inner sleeves to assist with identifying the best match for a release on Discogs. The user selects whether to do a sync from the database (on specific album(s)), sync the Discogs collection to the database, or both.

## Non-goals
This project will not implement
- Automatic submission of Discogs releases to the Discogs databse
- Recogniction of images of runouts from deadwax


## Functional Requirements
| Req # | Requirement | Status |
|-------|-------------|--------|
| FR-1  | Fetch user's collection from Discogs | In-progress | 
| FR-2  | Store raw and normalized Discogs data in a database | In-Progress |
| FR-3  | Separate Discogs data into groups by format | Planned |
| FR-4  | Read images of labels from a record and extract meta data | Planned |


## Non-functional Requirements

## Decisions made

## Assumptions

## Constraints

## Status and known gaps

## Testing 
