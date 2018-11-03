FROM python:3-slim-stretch

COPY requirements.txt /root/rankingbot/
COPY update_ranking.py /srv/rankingbot/
COPY update_ranking.sh /srv/rankingbot/

COPY crontab /root/rankingbot/

VOLUME /var/rankingbot

RUN /usr/local/bin/python3 -m pip install --no-cache-dir -r /root/rankingbot/requirements.txt \
    && chmod +x /srv/rankingbot/update_ranking.sh \
    && apt-get update \
    && apt-get -y install cron \
    && crontab /root/rankingbot/crontab \
    && rm -rf /root/rankingbot

CMD sed -i s/\$BOT_PW/${BOT_PW}/ /srv/rankingbot/update_ranking.sh \
    && cron && sleep infinity
