The Source Manager (SM) is part of a two app system, with the other app being the Data Sources (DS) App.


# Add, Update, and Delete

These are the core synchronization actions.

In order to propagate changes to DS, we synchronize additions, updates, and deletions of the following entities:
- Agencies
- Data Sources
- Meta URLs

Each action for each entity occurs through a separate task. At the moment, there are nine tasks total.

Each task gathers requisite information from the SM database and sends a request to one of nine corresponding endpoints in the DS API.

Each DS endpoint follows the following format:

```text
/v3/sync/{entity}/{action}
```

Synchronizations are designed to occur on an hourly basis.

Here is a high-level description of how each action works:

## Add

Adds the given entities to DS.

These are denoted with the `/{entity}/add` path in the DS API.

When an entity is added, it returns a unique DS ID that is mapped to the internal SM database ID via the DS app link tables.

For an entity to be added, it must meet preconditions which are distinct for each entity:
- Agencies: Must have an agency entry in the database and be linked to a location.
- Data Sources: Must be a URL that has been internally validated as a data source and linked to an agency.
- Meta URLs: Must be a URL that has been internally validated as a meta URL and linked to an agency.

## Update

Updates the given entities in DS.

These are denoted with the `/{entity}/update` path in the DS API.

These consist of submitting the updated entities (in full) to the requisite endpoint, and updating the local app link to indicate that the update occurred. All updates are designed to be full overwrites of the entity.

For an entity to be updated, it must meet preconditions which are distinct for each entity:
- Agencies: Must have either an agency row updated or an agency/location link updated or deleted.
- Data Sources: One of the following must be updated:
  - The URL table
  - The record type table
  - The optional data sources metadata table
  - The agency link table (either an addition or deletion)
- Meta URLs: Must be a URL that has been internally validated as a meta URL and linked to an agency.  Either the URL table or the agency link table (addition or deletion) must be updated.

## Delete

Deletes the given entities from DS.

These are denoted with the `/{entity}/delete` path in the DS API.

This consists of submitting a set of DS IDs to the requisite endpoint, and removing the associated DS app link entry in the SM database.

When an entity with a corresponding DS App Link is deleted from the Source Manager, the core data is removed but a deletion flag is appended to the DS App Link entry, indicating that the entry is not yet removed from the DS App. The deletion task uses this flag to identify entities to be deleted, submits the deletion request to the DS API, and removes both the flag and the DS App Link.