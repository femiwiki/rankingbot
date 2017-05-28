import csv
from collections import Counter
from datetime import datetime, timedelta

import mwclient as mw
import os

TIME_WINDOW = 15
SMOOTH_FACTOR = 0.1


def main():
    # Login to wiki
    wiki = Wiki(
        'femiwiki.com',
        '훈장봇',
        os.environ['BOT_PW'],
        '/opt/femiwiki/changes'
    )

    # Calculate score
    today = datetime.today().date()
    dates = enumerate_dates(today, TIME_WINDOW)
    counts_by_dates = [
        (date, count_for_a_day(wiki.get_recent_changes(date)))
        for date in dates
    ]
    scores = exponential_smoothing(counts_by_dates, SMOOTH_FACTOR)

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
    template.append('! 순위 !! 기여자 !! 평균 편집 횟수')
    for i, (score, user) in enumerate(scores[:15]):
        if i == 0:
            bg = '#e1e0f5'
        else:
            bg = 'transparent'

        template.append('|- style="background-color: %s"' % bg)
        template.append(
            '| style="text-align: right;" | %d '
            '|| [[사용자:%s|%s]] '
            '|| style="text-align: right;" | %.2f' % (i + 1, user, user, score))
    template.append('|}')

    # Update the page
    wiki.save(
        '페미위키:활동적인 사용자',
        '\n'.join(template),
        '활동적인 사용자 갱신'
    )


class Wiki:
    def __init__(self, url, user, pw, tempdir):
        self._site = mw.Site(url)
        self._user = user
        self._pw = pw
        self._tempdir = tempdir
        self._loggedin = False

    def login(self):
        if self._loggedin:
            return

        self._site.login(self._user, self._pw)
        self._loggedin = True

    def save(self, pagename, content, summary):
        self.login()
        page = self._site.pages[pagename]
        page.save(content, summary)

    def get_recent_changes(self, date):
        headers = ['timestamp', 'user', 'type', 'title']

        filename = os.path.join(self._tempdir, date.strftime('%Y%m%d'))
        if not os.path.isfile(filename):
            entries = self._fetch_recent_changes(date)
            with open(filename, 'w') as f:
                self._to_csv(f, entries, headers)
        with open(filename, 'r') as f:
            # Skip header
            f.readline()

            reader = csv.DictReader(f, headers)
            return [row for row in reader]

    def _fetch_recent_changes(self, date):
        self.login()

        changes = []
        rccontinue = None
        while True:
            result = self._site.api(
                'query',
                list='recentchanges',
                rctype='edit|new',
                rcshow='!bot|!anon',
                rcprop='timestamp|user|title',
                rclimit=5000,
                rcdir='newer',
                rcstart=date.strftime('%Y%m%d000000'),
                rcend=(date + timedelta(days=1)).strftime('%Y%m%d000000'),
                rccontinue=rccontinue,
            )
            changes += result['query']['recentchanges']
            if 'continue' not in result:
                break
            else:
                rccontinue = result['continue']['rccontinue']
        return changes

    @staticmethod
    def _to_csv(f, entries, fieldnames):
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)


def enumerate_dates(today, window):
    return [today - timedelta(days=i) for i in range(window, 0, -1)]


def count_for_a_day(changes):
    counter = Counter(c['user'] for c in changes)
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


if __name__ == '__main__':
    main()
