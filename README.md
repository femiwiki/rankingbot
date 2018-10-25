# ranking-bot

A bot that calculates the rankings of users with high contributions and displays
them on the front page of the [Femiwiki].

```bash
docker build --tag femiwiki/ranking-bot .

docker run --detach \
  --name ranking-bot \
  --restart always \
  --volume /var/ranking-bot:/var/ranking-bot:rw \
  -e "BOT_PW=xxxxxxxx" \
  femiwiki/ranking-bot
```

--------

The source code of *ranking-bot* is primarily distributed under the terms of
the [GNU Affero General Public License v3.0] or any later version. See
[COPYRIGHT] for details.

[ranking-bot]: https://femiwiki.com/w/%EC%82%AC%EC%9A%A9%EC%9E%90:%EB%9E%AD%ED%82%B9%EB%B4%87
[femiwiki]: https://femiwiki.com
[GNU Affero General Public License v3.0]: LICENSE
[COPYRIGHT]: COPYRIGHT
