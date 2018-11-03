#
# Build
#
FROM python:3-slim
WORKDIR /a
COPY setup.py .
COPY rankingbot rankingbot
RUN python setup.py bdist_wheel

#
# Run
#
FROM python:3-slim

# Set timezone
ENV TZ=Asia/Seoul
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Add Tini
# See https://github.com/krallin/tini for the further details
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
ENTRYPOINT ["/tini", "--"]

# Install cron
RUN apt-get update && apt-get -y install cron

# Register a cronjob
COPY crontab .
RUN crontab crontab && rm crontab

# Install dependencies
WORKDIR /a
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && rm requirements.txt

# Install rankingbot
COPY --from=0 /a/dist/*.whl .
RUN pip install --no-cache-dir rankingbot-*.whl

CMD echo "export RANKINGBOT_PASSWORD='$RANKINGBOT_PASSWORD'" > /a/env &&\
      touch /tmp/log &&\
      cron &&\
      tail -f /tmp/log
