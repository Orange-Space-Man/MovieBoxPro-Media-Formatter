import json
import re
import sqlite3
from pathlib import Path


MOVIEBOXPRO_DATABASE_PATH = Path.home() / "AppData" / "Roaming" / "MovieBoxPro" / "Data"
INVALID_FILENAME_CHARS = r'[<>:"/\\|?*\x00-\x1F]'

COLOR_GRAY = "\033[90m"
COLOR_RED = "\033[91m"
COLOR_GREEN = "\033[92m"
COLOR_RESET = "\033[0m"


def getDatabasePath():
    return MOVIEBOXPRO_DATABASE_PATH / "MovieBoxPro.db"


def cleanName(name):
    return re.sub(INVALID_FILENAME_CHARS, " ", str(name)).strip()

def formatId(tmdb_id):
    tmdb_id = str(tmdb_id).strip()

    if tmdb_id == "0":
        return f"{COLOR_RED}[tmdbid-{tmdb_id}] WARNING: TMDB ID IS 0{COLOR_RESET}"

    return f"[tmdbid-{tmdb_id}]"


def getStandardInfo(mdata, download_path):
    title = mdata.get("title", "Unknown Title")

    return {
        "title": title,
        "safe_title": cleanName(title) or "Unknown Title",
        "year": mdata.get("year", "Unknown Year"),
        "tmdb_id": mdata.get("tmdb_id", "Unknown TMDB ID"),
        "download_path": Path(download_path) if download_path else None,
    }


def getMedia():
    db = getDatabasePath()

    media = {
        "movies": [],
        "shows": [],
    }

    if not db.exists():
        print("Couldn't locate the database.")
        return media

    conn = None

    try:
        conn = sqlite3.connect(db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM DownloadLst;")
        rows = cursor.fetchall()

        for row in rows:
            try:
                mdata = json.loads(row[1]) if row[1] else {}
                sdata = json.loads(row[2]) if len(row) > 2 and row[2] else {}
                download_path = row[5] if len(row) > 5 and row[5] else None

                info = getStandardInfo(mdata, download_path)

                # if no season exists in mdata then treat it as a movie
                if mdata.get("season") is None:
                    print(
                        f"{COLOR_GRAY}Found MOVIE "
                        f"{info['safe_title']} {info['year']} "
                        f"{formatId(info['tmdb_id'])}"
                        f"{COLOR_RESET}"
                    )

                    media["movies"].append(info)
                    continue

                season = sdata.get("season", "Unknown season")
                episode = sdata.get("episode", "Unknown episode")
                episode_title = sdata.get("title", "Unknown title")

                info.update({
                    "season": season,
                    "episode": episode,
                    "episode_title": cleanName(episode_title) or "Unknown title",
                })

                print(
                    f"{COLOR_GRAY}Found SHOW "
                    f"{info['safe_title']} {info['year']} "
                    f"S{int(season):02}E{int(episode):02} "
                    f"{info['episode_title']} "
                    f"{formatId(info['tmdb_id'])}"
                    f"{COLOR_RESET}"
                )

                media["shows"].append(info)

            except (json.JSONDecodeError, IndexError, TypeError) as e:
                print(f"Error processing row: {e}")

    except sqlite3.Error as e:
        print(f"Failed to read from DownloadLst: {e}")

    finally:
        if conn:
            conn.close()

    return media


def formatMovie(info):
    title = info["safe_title"]
    year = info["year"]
    tmdb_id = info["tmdb_id"]
    path = info["download_path"]

    if not path:
        print(f"{COLOR_RED}Missing download_path for movie: {title}{COLOR_RESET}")
        return

    print(
        f"{COLOR_GRAY}Formatting MOVIE "
        f"{title} {year} {formatId(tmdb_id)}"
        f"{COLOR_RESET}"
    )

    new_name = f"{title} ({year}) [tmdbid-{tmdb_id}].mp4"
    new_path = path.parent.parent / new_name

    try:
        old_folder = path.parent

        path.rename(new_path)

        try:
            old_folder.rmdir()
        except OSError:
            pass

    except Exception as e:
        print(f"{COLOR_RED}Failed to format movie '{title}': {e}{COLOR_RESET}")


def formatShow(info):
    title = info["safe_title"]
    year = info["year"]
    tmdb_id = info["tmdb_id"]
    path = info["download_path"]

    season = int(info.get("season"))
    episode = int(info.get("episode"))
    episode_title = info.get("episode_title") or "Unknown title"

    if not path:
        print(
            f"{COLOR_RED}Missing download_path for show episode: "
            f"{title} S{season:02}E{episode:02}"
            f"{COLOR_RESET}"
        )
        return

    print(
        f"{COLOR_GRAY}Formatting SHOW "
        f"{title} {year} {episode_title} "
        f"S{season:02}E{episode:02} "
        f"{formatId(tmdb_id)}"
        f"{COLOR_RESET}"
    )

    show_folder = f"{title} ({year}) [tmdbid-{tmdb_id}]"
    season_folder = f"Season {season:02}"
    episode_name = f"{title} S{season:02}E{episode:02} - {episode_title}.mp4"

    new_path = path.parent.parent.parent.parent / show_folder / season_folder / episode_name

    try:
        new_path.parent.mkdir(parents=True, exist_ok=True)
        path.rename(new_path)

    except Exception as e:
        print(
            f"{COLOR_RED}Failed to format show "
            f"'{title}' S{season:02}E{episode:02}: {e}"
            f"{COLOR_RESET}"
        )


def formatMedia():
    media = getMedia()

    for movie in media["movies"]:
        formatMovie(movie)

    for show in media["shows"]:
        formatShow(show)

    input(f"\n{COLOR_GREEN}Complete, press enter to continue.{COLOR_RESET}")


if __name__ == "__main__":
    formatMedia()