# Updating the Nubra feature catalog

`current.json` is the source used by the lead agent. Every update must:

1. change `catalog_version`;
2. preserve the defined status meanings;
3. include a source for each changed capability;
4. copy the version into `history/<version>.json`;
5. update `manifest.json` with the file SHA-256; and
6. run `insights-publisher validate` before publishing.

Use `available` only for confirmed current public capability. Use `upcoming`, `partial`, or `internal_unverified` when access or release scope is uncertain. Suggestions belong under `not_available` until confirmed otherwise.

