import argparse
import collections
import datetime
import logging
import re
from os import environ

from .wiki import Wiki

logger = logging.getLogger(__name__)

TIME_WINDOW = 30
TOP_N = 15
SMOOTH_FACTOR = 0.1
DEBUG = environ.get("BOT_TEST", "0") == "1"
PASSWORD = environ["RANKINGBOT_PASSWORD"] if not DEBUG else ""
# Caps the bytes a single edit can add to the score, so that one large paste does not dominate the ranking
BYTES_CAP_PER_EDIT = 2000
CRITERIA = {
    "edits": "페미위키:활동적인 사용자/데이터",
    "bytes": "페미위키:활동적인 사용자/바이트 데이터",
}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="rankingbot")
    parser.add_argument(
        "--criterion",
        choices=CRITERIA.keys(),
        default="edits",
        help="what to rank users by: the number of edits, or the bytes added (default: edits)",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO)
    logger.info(f"Start updating the ranking by {args.criterion}")

    wiki = Wiki(
        "femiwiki.com",
        "랭킹봇@랭킹봇",
        PASSWORD,
        "./tmp",
        DEBUG,
    )

    # Calculate score
    today = datetime.datetime.now().astimezone().date()
    dates = enumerate_dates(today, TIME_WINDOW)

    content_namespaces = wiki.get_content_namespaces()
    counts_by_dates = []
    for date in dates:
        changes = wiki.get_recent_changes(date)
        if args.criterion == "bytes":
            counts = sum_bytes_for_a_day(changes, content_namespaces, BYTES_CAP_PER_EDIT)
        else:
            counts = count_for_a_day(changes, content_namespaces)
        counts_by_dates.append((date, counts))

    # Get top rankers
    p_exclude = r".*(\[\[분류\:활동적인 사용자 집계에서 제외할 사용자\]\]).*"
    blocked_users = [row["userid"] for row in wiki.get_blocked_accounts()]

    scores = exponential_smoothing(counts_by_dates, SMOOTH_FACTOR)
    scores_to_show = (
        (score, user)
        for score, user in scores
        if user != ""
        and int(user) not in blocked_users
        and not re.match(
            p_exclude,
            wiki.load(f"사용자:{wiki.userid_to_name(user)}"),
            re.DOTALL + re.MULTILINE,
        )
    )

    # Render wikitable
    template = []

    for i, (_, user) in zip(range(TOP_N), scores_to_show):
        name = wiki.userid_to_name(user)

        template.append("|-")
        template.append(f"| {i + 1} || [[특수:기여/{name}|{name}]] ")

    # Update the page
    wiki.save(CRITERIA[args.criterion], "\n".join(template), "활동적인 사용자 갱신")
    logger.info("Ranking update successfully finished")


def enumerate_dates(today, window):
    return [today - datetime.timedelta(days=i) for i in range(window, 0, -1)]


def count_for_a_day(changes, namespaces):
    counter = collections.Counter(c["userid"] for c in changes if int(c["ns"]) in namespaces)
    edits = [(user, freq) for user, freq in counter.items()]
    return sorted(edits, key=lambda row: row[1], reverse=True)


def sum_bytes_for_a_day(changes, namespaces, cap):
    # Only added bytes count; an edit that shrinks a page counts as zero rather than negative
    counter = collections.Counter()
    for c in changes:
        if int(c["ns"]) not in namespaces:
            continue
        added = int(c["newlen"] or 0) - int(c["oldlen"] or 0)
        counter[c["userid"]] += min(max(added, 0), cap)
    return sorted(counter.items(), key=lambda row: row[1], reverse=True)


def exponential_smoothing(counts_by_dates, smooth_factor):
    # Initialize score for all users
    scores = {}
    for _, counts in counts_by_dates:
        scores.update({user: 0 for user, _ in counts})

    # Calculate average count using exponential smoothing
    all_users = set(scores.keys())
    for date, counts in counts_by_dates:
        active_users = {user for user, _ in counts}
        inactive_users = all_users.difference(active_users)
        for user, freq in counts:
            scores[user] = scores[user] * (1 - smooth_factor) + freq * smooth_factor
        for user in inactive_users:
            scores[user] = scores[user] * (1 - smooth_factor)

    return sorted(((score, user) for user, score in scores.items()), reverse=True)
