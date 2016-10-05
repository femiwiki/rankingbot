import mwclient as mw
from collections import Counter
from itertools import chain
from datetime import datetime, timedelta
import operator
import os
import csv
import sys


TIME_WINDOW = 15
SMOOTH_FACTOR = 0.1

def main():
    wiki = Wiki(
        'femiwiki.com',
        '훈장봇',
        os.environ['BOT_PW'],
        '/opt/femiwiki/changes'
    )

    today = datetime.today().date()
    dates = [today - timedelta(days=i) for i in range(TIME_WINDOW, 0, -1)]

    counters = {}
    for date in dates:
        counters[date] = Counter(
            sorted(entry['user'] for entry in wiki.get_recent_changes(date))
        )

    users = set(chain(*[c.elements() for c in counters.values()]))
    scores = dict(zip(users, [0.0] * len(users)))
    for date in dates:
        counter = counters[date]
        active_users = set(counter.elements())
        inactive_users = users.difference(active_users)
        for user in active_users:
            scores[user] = scores[user] * (1 - SMOOTH_FACTOR) + counter[user] * SMOOTH_FACTOR
        for user in inactive_users:
            scores[user] = scores[user] * (1 - SMOOTH_FACTOR) + counter[user] * SMOOTH_FACTOR

    template = []
    template.append('최근 %d일 동안 일 평균 편집 횟수 기준 최다 기여자 순위입니다. 최근 활동에 가중치를 부여하기 위해 [[지수평활법]](계수 %.2f)으로 계산합니다. ([[페미위키:업적 시스템|업적 시스템]] 참고)' % (TIME_WINDOW, SMOOTH_FACTOR))

    template.append('{| class="wikitable" style="width: 100%"')
    template.append('|-')
    template.append('! 순위 !! 기여자 !! 평균 편집 횟수')
    for i, (user, score) in enumerate(sorted(scores.items(), key=operator.itemgetter(1), reverse=True)[:15]):
        if i == 0:
            bg = '#e1e0f5'
        else:
            bg = 'transparent'

        template.append('|- style="background-color: %s"' % bg)
        template.append('| style="text-align: right;" | %d || [[사용자:%s|%s]] || style="text-align: right;" | %.2f' % ((i+1), user, user, score))
    template.append('|}')

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
            entries = self.fetch_recent_changes(date)
            with open(filename, 'w') as f:
                self._to_csv(f, entries, headers)
        with open(filename, 'r') as f:
            # Skip header
            f.readline()

            reader = csv.DictReader(f, headers)
            return [row for row in reader]

    def fetch_recent_changes(self, date):
        self.login()

        changes = []
        rccontinue=None
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
                rccontinue=result['continue']['rccontinue']
        return changes

    @staticmethod
    def _to_csv(f, entries, fieldnames):
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)


if __name__ == '__main__':
    main()
