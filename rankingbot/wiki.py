import csv
import logging
import pathlib
from datetime import timedelta
from os import path
from time import sleep

import mwclient

logger = logging.getLogger(__name__)


class Wiki:
    def __init__(self, url, user, pw, tempdir, prevent_save):
        self._url = url
        self._site = mwclient.Site(url, path='/')
        self._user = user
        self._pw = pw
        self._tempdir = tempdir
        self._loggedin = False
        self._prevent_save = prevent_save

    def login(self):
        if self._loggedin:
            return

        self._site.login(self._user, self._pw)
        self._loggedin = True
        logger.info('Logged in')

    def load(self, pagename):
        self.login()
        page = self._site.pages[pagename]
        return page.text()

    def get_blocked_accounts(self):
        result = self._site.api(
            'query',
            list='blocks',
            bklimit='max',
            bkprop='userid',
            bkshow='account',
            format='json',
        )

        return result['query']['blocks']

    def save(self, pagename, content, summary):
        if self._prevent_save:
            print('Updating page: %s' % pagename)
            print('Summary: %s' % summary)
            print('Content:\n')
            print(content)
        else:
            self.login()
            page = self._site.pages[pagename]
            page.save(content, summary)

    def get_recent_changes(self, date):
        headers = ['timestamp', 'userid', 'type', 'title']

        filename = path.join(self._tempdir, 'rc-cache', date.strftime('%Y%m%d'))
        if not path.isfile(filename):
            entries = self._fetch_recent_changes(date)
            pathlib.Path(self._tempdir).mkdir(parents=True, exist_ok=True)
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
            logger.info(f'Requesting recent changes... ({date}, {rccontinue})')
            result = self._site.api(
                'query',
                list='recentchanges',
                rctype='edit|new',
                rcshow='!bot|!anon',
                rcprop='timestamp|userid|title',
                rclimit='max',
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

        sleep(5)
        return changes

    def userid_to_name(self, id):
        result = self._site.api(
            'query',
            list='users',
            ususerids=id
        )
        return result['query']['users'][0]['name']

    @staticmethod
    def _to_csv(f, entries, fieldnames):
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        w.writeheader()
        for entry in entries:
            w.writerow(entry)
