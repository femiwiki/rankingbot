[rankingbot]
========
A bot that calculates the rankings of users with high contributions and displays
them on the front page of the [Femiwiki].

```bash
docker run --detach \
  --name rankingbot \
  --restart always \
  --volume /var/rankingbot:/var/rankingbot:rw \
  -e 'BOT_PW=xxxxxxxx' \
  femiwiki/rankingbot
```

&nbsp;

--------

The source code of *rankingbot* is primarily distributed under the terms of
the [GNU Affero General Public License v3.0] or any later version. See
[COPYRIGHT] for details.

[rankingbot]: https://femiwiki.com/w/%EC%82%AC%EC%9A%A9%EC%9E%90:%EB%9E%AD%ED%82%B9%EB%B4%87
[Femiwiki]: https://femiwiki.com
[GNU Affero General Public License v3.0]: LICENSE
[COPYRIGHT]: COPYRIGHT
