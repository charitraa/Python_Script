"""
Instagram Profile Scraper

Collects everything that is publicly visible on an Instagram profile and writes
it to disk in a structured, reusable form:

  * Profile details ...... username, full name, biography, follower / following
                           counts, post count, category, external URL, verified
                           and business flags, profile picture URL.
  * Profile picture ...... downloaded in full resolution (the account "logo").
  * Posts ................ every post with its caption, hashtags, mentions,
                           like / comment counts, timestamp, location, media
                           type and the direct URL of every image or video
                           (carousel posts are expanded into their child items).
  * Comments ............. the top comments of each post (needs a login).
  * Highlights ........... every highlight tray, its title, cover image and the
                           individual story items inside it (needs a login).

Output layout (under OUTPUT_DIR / <username>):

    <username>/
        profile.json            profile details
        posts.json              full post data
        posts.csv               flattened post data, one row per post
        highlights.json         highlight trays and their items
        profile_pic/            downloaded profile picture
        posts_media/            downloaded post images / videos
        highlights_media/       downloaded highlight images / videos

Requirements
------------
    pip install instaloader

Login (optional but recommended)
--------------------------------
Anonymous access works for a public profile's details and posts, but Instagram
rate limits it aggressively and hides highlights and comments entirely. To log
in, export a session once and reuse it afterwards:

    instaloader --login YOUR_USERNAME        # asks for the password once
    export IG_USERNAME=YOUR_USERNAME         # this script picks the session up

Never hardcode a password in this file; the script only reads IG_USERNAME and
the session file that the command above creates.

Example usage
-------------
    python 2026-09-03_instagram_profile_scraper.py
    python 2026-09-03_instagram_profile_scraper.py --username horaa_storeofficial
    python 2026-09-03_instagram_profile_scraper.py --max-posts 25 --no-media
    python 2026-09-03_instagram_profile_scraper.py --output ~/ig_data --delay 4

Please scrape responsibly: only public data, keep the request rate low, and
respect Instagram's Terms of Service and the account owner's rights.
"""

import argparse
import csv
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import instaloader
    from instaloader.exceptions import (
        ConnectionException,
        LoginRequiredException,
        PrivateProfileNotFollowedException,
        ProfileNotExistsException,
        QueryReturnedBadRequestException,
        TooManyRequestsException,
    )
except ImportError:  # pragma: no cover - dependency hint for first-time users
    sys.exit("Missing dependency. Install it with:  pip install instaloader")

# --- Configuration Variables ---
# The account to scrape: https://www.instagram.com/horaa_storeofficial/
TARGET_USERNAME = "horaa_storeofficial"

# Where the per-account folder is created.
OUTPUT_DIR = Path.home() / "instagram_scrapes"

# Your own Instagram username, used only to load a saved session file created
# by `instaloader --login <user>`. Leave unset to browse anonymously.
LOGIN_USERNAME = os.environ.get("IG_USERNAME")

# Download the actual image / video files, not just their URLs.
DOWNLOAD_MEDIA = True

# Stop after this many posts (None = every post on the profile).
MAX_POSTS = None

# Top-level comments to fetch per post (0 disables it; needs a login).
MAX_COMMENTS_PER_POST = 20

# Seconds to wait between posts. Instagram throttles fast clients, so keep this
# at 2 seconds or more when scraping a large account.
REQUEST_DELAY = 2.0

# --- Logger Setup ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def build_loader(download_media: bool) -> instaloader.Instaloader:
    """
    Creates the Instaloader client used for every request.

    Args:
        download_media (bool): Whether media files should be written to disk.

    Returns:
        instaloader.Instaloader: A configured client.
    """
    return instaloader.Instaloader(
        download_pictures=download_media,
        download_videos=download_media,
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,   # comments are fetched manually, see below
        save_metadata=False,       # this script writes its own JSON
        compress_json=False,
        post_metadata_txt_pattern="",
        max_connection_attempts=3,
        quiet=True,
    )


def try_login(loader: instaloader.Instaloader, username: str | None) -> bool:
    """
    Loads a previously saved Instaloader session, if one exists.

    Args:
        loader (instaloader.Instaloader): The client to authenticate.
        username (str | None): Your own Instagram username, or None.

    Returns:
        bool: True when the session was loaded, False for anonymous access.
    """
    if not username:
        logger.info("No IG_USERNAME set - continuing anonymously "
                    "(highlights and comments will be skipped).")
        return False

    try:
        loader.load_session_from_file(username)
        logger.info("Loaded saved session for '%s'.", username)
        return True
    except FileNotFoundError:
        logger.warning(
            "No session file for '%s'. Create one with:  instaloader --login %s",
            username, username,
        )
    except Exception as exc:  # pragma: no cover - depends on local session state
        logger.warning("Could not load the session for '%s': %s", username, exc)
    return False


def scrape_profile_details(profile: instaloader.Profile) -> dict:
    """
    Collects the profile's own metadata.

    Args:
        profile (instaloader.Profile): The loaded profile.

    Returns:
        dict: The profile fields, ready to be serialised as JSON.
    """
    return {
        "userid": profile.userid,
        "username": profile.username,
        "full_name": profile.full_name,
        "biography": profile.biography,
        "biography_hashtags": list(profile.biography_hashtags),
        "biography_mentions": list(profile.biography_mentions),
        "external_url": profile.external_url,
        "followers": profile.followers,
        "followees": profile.followees,
        "media_count": profile.mediacount,
        "igtv_count": profile.igtvcount,
        "is_private": profile.is_private,
        "is_verified": profile.is_verified,
        "is_business_account": profile.is_business_account,
        "business_category_name": profile.business_category_name,
        "profile_url": f"https://www.instagram.com/{profile.username}/",
        "profile_pic_url": profile.profile_pic_url,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def download_profile_pic(loader: instaloader.Instaloader,
                         profile: instaloader.Profile,
                         target_dir: Path) -> str | None:
    """
    Downloads the profile picture (the account's logo) in full resolution.

    Args:
        loader (instaloader.Instaloader): The client to download with.
        profile (instaloader.Profile): The loaded profile.
        target_dir (Path): Folder that will hold the image.

    Returns:
        str | None: The path of the saved file, or None if it failed.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    stem = target_dir / f"{profile.username}_profile_pic"
    try:
        loader.download_pic(str(stem), profile.profile_pic_url,
                            datetime.now())
        saved = next(iter(sorted(target_dir.glob(f"{stem.name}.*"))), None)
        if saved:
            logger.info("Saved profile picture -> %s", saved)
            return str(saved)
    except Exception as exc:
        logger.error("Could not download the profile picture: %s", exc)
    return None


def serialize_post(post: instaloader.Post, max_comments: int) -> dict:
    """
    Turns a single post into a plain dictionary.

    Carousel posts ("sidecars") are expanded so that every image or video in
    the carousel appears in the `media` list with its own direct URL.

    Args:
        post (instaloader.Post): The post to describe.
        max_comments (int): How many top-level comments to fetch (0 = none).

    Returns:
        dict: All available fields for this post.
    """
    media = []
    if post.typename == "GraphSidecar":
        for index, node in enumerate(post.get_sidecar_nodes(), start=1):
            media.append({
                "index": index,
                "is_video": node.is_video,
                "image_url": node.display_url,
                "video_url": node.video_url if node.is_video else None,
            })
    else:
        media.append({
            "index": 1,
            "is_video": post.is_video,
            "image_url": post.url,
            "video_url": post.video_url if post.is_video else None,
        })

    comments = []
    if max_comments > 0:
        try:
            for comment in post.get_comments():
                comments.append({
                    "id": comment.id,
                    "author": comment.owner.username,
                    "text": comment.text,
                    "created_at": comment.created_at_utc.isoformat(),
                    "likes": getattr(comment, "likes_count", None),
                })
                if len(comments) >= max_comments:
                    break
        except (LoginRequiredException, QueryReturnedBadRequestException) as exc:
            logger.debug("Comments unavailable for %s: %s", post.shortcode, exc)

    location = None
    try:
        if post.location:
            location = {
                "id": post.location.id,
                "name": post.location.name,
                "lat": post.location.lat,
                "lng": post.location.lng,
            }
    except (LoginRequiredException, KeyError):
        pass  # location needs a login on many posts

    return {
        "shortcode": post.shortcode,
        "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
        "mediaid": post.mediaid,
        "typename": post.typename,           # GraphImage / GraphVideo / GraphSidecar
        "is_video": post.is_video,
        "date_utc": post.date_utc.isoformat(),
        "caption": post.caption or "",
        "hashtags": list(post.caption_hashtags),
        "mentions": list(post.caption_mentions),
        "tagged_users": list(post.tagged_users),
        "likes": post.likes,
        "comment_count": post.comments,
        "video_view_count": post.video_view_count if post.is_video else None,
        "video_duration": post.video_duration if post.is_video else None,
        "accessibility_caption": post.accessibility_caption,
        "is_sponsored": post.is_sponsored,
        "location": location,
        "media_count": len(media),
        "media": media,
        "comments": comments,
    }


def scrape_posts(loader: instaloader.Instaloader,
                 profile: instaloader.Profile,
                 media_dir: Path,
                 download_media: bool,
                 max_posts: int | None,
                 max_comments: int,
                 delay: float) -> list[dict]:
    """
    Walks through the profile's posts, newest first.

    Args:
        loader (instaloader.Instaloader): The client to download with.
        profile (instaloader.Profile): The loaded profile.
        media_dir (Path): Folder for the downloaded image / video files.
        download_media (bool): Whether to save the media files themselves.
        max_posts (int | None): Stop after this many posts, or None for all.
        max_comments (int): Comments to fetch per post.
        delay (float): Seconds to wait between posts.

    Returns:
        list[dict]: One dictionary per post.
    """
    if download_media:
        media_dir.mkdir(parents=True, exist_ok=True)

    posts: list[dict] = []
    for post in profile.get_posts():
        try:
            record = serialize_post(post, max_comments)
        except (ConnectionException, QueryReturnedBadRequestException) as exc:
            logger.warning("Skipping post %s: %s", post.shortcode, exc)
            continue

        posts.append(record)
        logger.info("Post %d/%s  %s  %s  %d likes",
                    len(posts),
                    max_posts if max_posts else profile.mediacount,
                    record["date_utc"][:10],
                    record["shortcode"],
                    record["likes"] or 0)

        if download_media:
            try:
                loader.download_post(post, target=str(media_dir))
            except Exception as exc:
                logger.warning("Media download failed for %s: %s",
                               post.shortcode, exc)

        if max_posts and len(posts) >= max_posts:
            break
        time.sleep(delay)

    return posts


def scrape_highlights(loader: instaloader.Instaloader,
                      profile: instaloader.Profile,
                      media_dir: Path,
                      download_media: bool,
                      delay: float) -> list[dict]:
    """
    Collects the profile's story highlights. Requires a logged-in session.

    Args:
        loader (instaloader.Instaloader): The authenticated client.
        profile (instaloader.Profile): The loaded profile.
        media_dir (Path): Folder for the downloaded highlight media.
        download_media (bool): Whether to save the media files themselves.
        delay (float): Seconds to wait between highlight trays.

    Returns:
        list[dict]: One dictionary per highlight tray.
    """
    if download_media:
        media_dir.mkdir(parents=True, exist_ok=True)

    highlights: list[dict] = []
    try:
        for highlight in loader.get_highlights(profile):
            items = []
            for item in highlight.get_items():
                items.append({
                    "mediaid": item.mediaid,
                    "typename": item.typename,
                    "is_video": item.is_video,
                    "date_utc": item.date_utc.isoformat(),
                    "image_url": item.url,
                    "video_url": item.video_url if item.is_video else None,
                })

            highlights.append({
                "unique_id": highlight.unique_id,
                "title": highlight.title,
                "cover_url": highlight.cover_url,
                "item_count": len(items),
                "items": items,
            })
            logger.info("Highlight '%s' - %d items", highlight.title, len(items))

            if download_media:
                tray_dir = media_dir / _safe_name(highlight.title)
                tray_dir.mkdir(parents=True, exist_ok=True)
                for item in highlight.get_items():
                    try:
                        loader.download_storyitem(item, target=str(tray_dir))
                    except Exception as exc:
                        logger.warning("Highlight item %s failed: %s",
                                       item.mediaid, exc)
            time.sleep(delay)

    except LoginRequiredException:
        logger.warning("Highlights need a logged-in session - skipping them. "
                       "Run:  instaloader --login <your_username>")
    except Exception as exc:
        logger.error("Could not read the highlights: %s", exc)

    return highlights


def _safe_name(text: str) -> str:
    """
    Makes a string safe to use as a folder name.

    Args:
        text (str): The raw title.

    Returns:
        str: A filesystem-friendly version of it.
    """
    cleaned = "".join(c if c.isalnum() or c in " -_" else "_" for c in text)
    return cleaned.strip().replace(" ", "_") or "untitled"


def save_json(data, path: Path) -> None:
    """
    Writes any JSON-serialisable object to disk as UTF-8.

    Args:
        data: The object to write.
        path (Path): Destination file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    logger.info("Wrote %s", path)


def save_posts_csv(posts: list[dict], path: Path) -> None:
    """
    Writes a flattened, spreadsheet-friendly version of the posts.

    Args:
        posts (list[dict]): The scraped posts.
        path (Path): Destination CSV file.
    """
    if not posts:
        logger.warning("No posts to write to CSV.")
        return

    columns = [
        "shortcode", "post_url", "date_utc", "typename", "is_video",
        "likes", "comment_count", "video_view_count", "media_count",
        "caption", "hashtags", "mentions", "location_name", "image_urls",
        "video_urls",
    ]

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for post in posts:
            writer.writerow({
                "shortcode": post["shortcode"],
                "post_url": post["post_url"],
                "date_utc": post["date_utc"],
                "typename": post["typename"],
                "is_video": post["is_video"],
                "likes": post["likes"],
                "comment_count": post["comment_count"],
                "video_view_count": post["video_view_count"],
                "media_count": post["media_count"],
                "caption": post["caption"].replace("\n", " ").strip(),
                "hashtags": " ".join(post["hashtags"]),
                "mentions": " ".join(post["mentions"]),
                "location_name": (post["location"] or {}).get("name", ""),
                "image_urls": " | ".join(m["image_url"] for m in post["media"]
                                         if m["image_url"]),
                "video_urls": " | ".join(m["video_url"] for m in post["media"]
                                         if m["video_url"]),
            })
    logger.info("Wrote %s (%d rows)", path, len(posts))


def scrape_account(username: str,
                   output_root: Path,
                   download_media: bool = DOWNLOAD_MEDIA,
                   max_posts: int | None = MAX_POSTS,
                   max_comments: int = MAX_COMMENTS_PER_POST,
                   delay: float = REQUEST_DELAY,
                   login_username: str | None = LOGIN_USERNAME) -> dict:
    """
    Runs the whole scrape for one account and writes every output file.

    Args:
        username (str): The Instagram handle to scrape, without the '@'.
        output_root (Path): Folder that will contain the per-account folder.
        download_media (bool): Save the image / video files themselves.
        max_posts (int | None): Stop after this many posts, or None for all.
        max_comments (int): Comments to fetch per post.
        delay (float): Seconds to wait between requests.
        login_username (str | None): Your own handle, for the saved session.

    Returns:
        dict: A summary of what was collected.
    """
    target_dir = output_root / username
    target_dir.mkdir(parents=True, exist_ok=True)

    loader = build_loader(download_media)
    logged_in = try_login(loader, login_username)

    logger.info("Loading profile '%s' ...", username)
    profile = instaloader.Profile.from_username(loader.context, username)

    details = scrape_profile_details(profile)
    details["logged_in_session"] = logged_in
    logger.info("%s - %d followers, %d posts",
                profile.username, profile.followers, profile.mediacount)

    if download_media:
        details["profile_pic_path"] = download_profile_pic(
            loader, profile, target_dir / "profile_pic")
    save_json(details, target_dir / "profile.json")

    if profile.is_private and not profile.followed_by_viewer:
        logger.warning("This profile is private and the session does not "
                       "follow it - only the public details above are "
                       "available.")
        return {"profile": details, "posts": [], "highlights": []}

    posts = scrape_posts(loader, profile, target_dir / "posts_media",
                         download_media, max_posts,
                         max_comments if logged_in else 0, delay)
    save_json(posts, target_dir / "posts.json")
    save_posts_csv(posts, target_dir / "posts.csv")

    highlights: list[dict] = []
    if logged_in:
        highlights = scrape_highlights(loader, profile,
                                       target_dir / "highlights_media",
                                       download_media, delay)
        save_json(highlights, target_dir / "highlights.json")
    else:
        logger.info("Skipping highlights - they are only visible to a "
                    "logged-in session.")

    logger.info("Done. %d posts and %d highlights saved under %s",
                len(posts), len(highlights), target_dir)
    return {"profile": details, "posts": posts, "highlights": highlights}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """
    Parses the command line options.

    Args:
        argv (list[str] | None): Argument list, or None to read sys.argv.

    Returns:
        argparse.Namespace: The parsed options.
    """
    parser = argparse.ArgumentParser(
        description="Scrape an Instagram profile's details, posts and "
                    "highlights into JSON / CSV files.")
    parser.add_argument("--username", default=TARGET_USERNAME,
                        help=f"Account to scrape (default: {TARGET_USERNAME})")
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR,
                        help=f"Output folder (default: {OUTPUT_DIR})")
    parser.add_argument("--max-posts", type=int, default=MAX_POSTS,
                        help="Stop after this many posts (default: all)")
    parser.add_argument("--max-comments", type=int, default=MAX_COMMENTS_PER_POST,
                        help="Comments to fetch per post (needs a login)")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY,
                        help="Seconds to wait between requests")
    parser.add_argument("--no-media", action="store_true",
                        help="Only collect metadata and URLs, download nothing")
    parser.add_argument("--login-user", default=LOGIN_USERNAME,
                        help="Your own handle, to load its saved session")
    return parser.parse_args(argv)


def main() -> int:
    """
    Entry point: scrapes the configured account and reports the outcome.

    Returns:
        int: 0 on success, 1 on a handled failure.
    """
    args = parse_args()
    username = args.username.strip().strip("/").split("/")[-1].lstrip("@")

    try:
        scrape_account(
            username=username,
            output_root=args.output.expanduser(),
            download_media=not args.no_media,
            max_posts=args.max_posts,
            max_comments=args.max_comments,
            delay=args.delay,
            login_username=args.login_user,
        )
    except ProfileNotExistsException:
        logger.error("No such profile: '%s'", username)
        return 1
    except PrivateProfileNotFollowedException:
        logger.error("'%s' is private and your session does not follow it.",
                     username)
        return 1
    except (TooManyRequestsException, QueryReturnedBadRequestException):
        logger.error("Instagram is rate limiting this client. Wait a while, "
                     "raise --delay, and log in with a session file.")
        return 1
    except LoginRequiredException:
        logger.error("Instagram now requires a login for this request. Run:  "
                     "instaloader --login <your_username>")
        return 1
    except ConnectionException as exc:
        logger.error("Network / Instagram error: %s", exc)
        return 1
    except KeyboardInterrupt:
        logger.warning("Interrupted - partial results were kept.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
