# Camera Studio roadmap

Camera Studio is a proposed native iPhone and iPad app for reviewing a Sony camera shoot, editing selected RAW photos, and archiving a project on the NAS. It shares the Pi with Personal Library and keeps its own project catalog.

## From camera to archive

1. Open a Sony Alpha 7C over USB or import from a card reader. Use embedded previews for fast browsing and full RAW renders for focus checks.
2. Organize the shoot into a project. Review photos fullscreen and record picks, ratings, and tags.
3. Adjust exposure, highlights, shadows, and white balance. Store edits as recipes and preserve the original ARW files.
4. Apply a shared look to selected photos, review the set together, and refine individual photos.
5. Upload originals, recipes, and rendered exports to the Pi. Verify checksums and resume interrupted transfers.
6. Publish selected finished exports to Immich. Track whether Immich has indexed each export so it can be opened in the mobile app.

## First milestones

| Milestone | Completion check |
| --- | --- |
| Camera and RAW feasibility | Open real ARW files, zoom into a full-resolution render, and handle camera disconnection on iPhone and iPad. |
| Local review and editing | Picks and recipes survive relaunch. Export appearance matches the reviewed render. |
| Project archive | Retries preserve a single copy of each original. Restore a project with its originals and recipes. |
| Immich publication | Open the intended finished export in Immich on both iPhone and iPad. Each subsequent export version can be published independently. |
