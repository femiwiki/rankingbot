FROM python:3-slim-stretch

COPY requirements.txt /root/ranking-bot/
COPY update_ranking.py /srv/ranking-bot/
COPY update_ranking.sh /srv/ranking-bot/

COPY crontab /root/ranking-bot/

VOLUME /var/ranking-bot

RUN /usr/local/bin/python3 -m pip install --no-cache-dir -r /root/ranking-bot/requirements.txt \
    && chmod +x /srv/ranking-bot/update_ranking.sh \
    && apt-get update \
    && apt-get -y install cron \
    && crontab /root/ranking-bot/crontab \
    && rm -rf /root/ranking-bot

CMD sed -i s/\$BOT_PW/${BOT_PW}/ /srv/ranking-bot/update_ranking.sh \
    && cron && sleep infinity
