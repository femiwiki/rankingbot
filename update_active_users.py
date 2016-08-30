import mwclient as mw
from collections import Counter
from datetime import datetime, timedelta
import os


def main():
    site = mw.Site('femiwiki.com')
    site.login('훈장봇', os.environ['BOT_PW'])

    now = datetime.now()
    entries = fetch_recent_changes(
        site,
        now - timedelta(days=7),
        now,
    )
    counts = Counter(sorted(entry['user'] for entry in entries)).most_common(20)
    page = site.pages['페미위키:활동적인 사용자']
    template = []
    template.append('== 활동적인 사용자 ==')
    for user, n in counts:
        template.append('# [[사용자:%s|%s]]: <span class="count">%d</span>회' % (user, user, n))
    page.save('\n'.join(template), '활동적인 사용자 갱신')


def fetch_recent_changes(site, date_from, date_to):
    changes = []
    rccontinue=None
    while True:
        result = site.api(
            'query',
            list='recentchanges',
            rctype='edit|new',
            rcshow='!bot|!anon',
            rcprop='timestamp|user|title',
            rclimit=5000,
            rcdir='newer',
            rcstart=date_from.strftime('%Y%m%d%H%M%S'),
            rcend=date_to.strftime('%Y%m%d%H%M%S'),
            rccontinue=rccontinue,
        )
        changes += result['query']['recentchanges']
        if 'continue' not in result:
            break
        else:
            rccontinue=result['continue']['rccontinue']
    return changes



if __name__ == '__main__':
    main()
