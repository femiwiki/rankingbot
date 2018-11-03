import re
import datetime
import logging
import collections
from os import environ

from .wiki import Wiki

logger = logging.getLogger(__name__)

TIME_WINDOW = 30
TOP_N = 15
SMOOTH_FACTOR = 0.1
PASSWORD = environ['RANKINGBOT_PASSWORD']
DEBUG = environ.get('BOT_TEST', '0') == '1'


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info('Start updating the ranking')

    wiki = Wiki(
        'femiwiki.com',
        '랭킹봇@랭킹봇',
        PASSWORD,
        './tmp',
        DEBUG,
    )

    # Calculate score
    today = datetime.datetime.today().date()
    dates = enumerate_dates(today, TIME_WINDOW)
    counts_by_dates = [
        (date, count_for_a_day(wiki.get_recent_changes(date)))
        for date in dates
    ]

    # Get top rankers
    p_exclude = r'.*(\[\[분류\:활동적인 사용자 집계에서 제외할 사용자\]\]).*'
    blocked_users = [row['id'] for row in wiki.get_blocked_accounts()]

    scores = exponential_smoothing(counts_by_dates, SMOOTH_FACTOR)
    scores_to_show = (
        (score, user) for score, user in scores
        if user not in blocked_users and not re.match(
            p_exclude,
            wiki.load('사용자:%s' % wiki.userid_to_name(user)),
            re.DOTALL + re.MULTILINE,
        )
    )

    # Render wikitable
    template = []
    template.append(
        '최근 %d일 동안 일 평균 편집 횟수 기준 최다 기여자 순위입니다. 최근 '
        '활동에 가중치를 부여하기 위해 [[지수평활법]](계수 %.2f)으로 '
        '계산합니다. ([[페미위키:업적 시스템|업적 시스템]] 참고)' % (
            TIME_WINDOW, SMOOTH_FACTOR
        ))

    template.append('{| style="width: 100%"')
    template.append('|-')
    template.append('! 순위 !! 기여자')
    for i, (score, user) in zip(range(TOP_N), scores_to_show):
        bg = 'transparent'
        name = wiki.userid_to_name(user)

        template.append('|- style="background-color: %s"' % bg)
        template.append(
            '| style="text-align: right;" | %d '
            '|| [[사용자:%s|%s]] ' % (i + 1, name, name))
    template.append('|}')

    # Update the page
    wiki.save(
        '페미위키:활동적인 사용자',
        '\n'.join(template),
        '활동적인 사용자 갱신'
    )
    logger.info('Ranking update successfully finished')


def enumerate_dates(today, window):
    return [today - datetime.timedelta(days=i) for i in range(window, 0, -1)]


def count_for_a_day(changes):
    counter = collections.Counter(c['userid'] for c in changes)
    edits = [
        (user, freq) for user, freq in counter.items()
    ]
    return sorted(edits, key=lambda row: row[1], reverse=True)


def exponential_smoothing(counts_by_dates, smooth_factor):
    # Initialize score for all users
    scores = {}
    for _, counts in counts_by_dates:
        scores.update(dict((user, 0) for user, _ in counts))

    # Calculate average count using exponential smoothing
    all_users = set(scores.keys())
    for date, counts in counts_by_dates:
        active_users = set(user for user, _ in counts)
        inactive_users = all_users.difference(active_users)
        for user, freq in counts:
            scores[user] = (
                scores[user] * (1 - smooth_factor) +
                freq * smooth_factor
            )
        for user in inactive_users:
            scores[user] = scores[user] * (1 - smooth_factor)

    return sorted(
        ((score, user) for user, score in scores.items()),
        reverse=True
    )