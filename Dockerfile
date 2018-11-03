FROM python:3-slim-stretch

# Install cron
RUN apt-get update && apt-get -y install cron

# Register a cronjob
COPY crontab .
RUN crontab crontab && rm crontab

# Install dependencies
WORKDIR /a
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

COPY update_ranking.py .

CMD echo "export RANKINGBOT_PASSWORD='$RANKINGBOT_PASSWORD'" > /a/env &&\
      cron &&\
      sleep infinity
