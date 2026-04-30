# MovieBoxPro Media Organizer

A small Python utility that reads your local MovieBoxPro download database and renames/moves downloaded media into a cleaner folder structure for media servers like **Plex** and **Jellyfin**.

This tool does **not** download media. It only organizes media that already exists on your machine.

This is a continuation of a previously archived project, [MBPConv](https://github.com/BoldlyGo88/MBPConv/tree/main)

### Movie Format

Movies are renamed like this:

```text
Movie Title (2024) [tmdbid-12345].mp4
```

### TV Show Format

TV episodes are moved into a show/season folder structure like this:

```text
Show Title (2024) [tmdbid-12345]/
└── Season 01/
    └── Show Title S01E02 - Episode Title.mp4
```

The script also highlights entries in red when the TMDB ID is `0`, since this will require manually obtaining the ID from TMDB.

## Requirements

- Windows
- Python 3.8+
- MovieBoxPro installed
- Downloaded MovieBoxPro media already present on your system
- Access to the local MovieBoxPro database:

```text
%APPDATA%\MovieBoxPro\Data\MovieBoxPro.db
```

No external Python packages are required.

The script only uses Python standard-library modules:

- `sqlite3`
- `json`
- `re`
- `pathlib`

## How to Use

1. Save the script
2. Make sure nothing is currently downloading on MovieBoxPro
4. Make sure there are no stale/deleted/removed downloads in MovieBoxPro's download section (within the application) as this will cause errors when reading the MovieBoxPro.db
5. Double click or run the script through Command Prompt
6. The script will scan the MovieBoxPro download database and print the media it finds.
7. It will then rename/move the downloaded files into the expected movie or TV folder format.

MovieBoxPro by default downloads to C:\Users\<your_user>\Videos\MovieBoxPro but this script should support custom locations as it pulls directly from the download_path in the MovieBoxPro.db

## Notes

- Entries with `tmdbid-0` should be checked manually.
- This tool modifies file paths directly, so it is recommended to test with a small sample first.

## Things to Know

This tool is intended only for organizing files already downloaded.

It does not:

- Download media
- Scrape media
- Bypass DRM
- Access MovieBoxPro servers
- Modify the MovieBoxPro application (you will need to still delete download entries within the app, otherwise you will have stale entries in the MovieBoxPro.db file)

## License

This project is licensed under the [MIT License](LICENSE.md)
