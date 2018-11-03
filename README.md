[rankingbot]
========
A bot that calculates the rankings of users with high contributions and displays
them on the front page of the [Femiwiki].

```bash
docker run --detach \
  --name rankingbot \
  --restart always \
  -e 'RANKINGBOT_PASSWORD=xxxxxxxx' \
  femiwiki/rankingbot
```

You have to grant [`(protect)`] permission to the bot.

&nbsp;

Instructions
--------
Development
```bash
# Setup venv first

pip install -r requirements.txt

export RANKINGBOT_PASSWORD=xxxxxxxx
python update_ranking.py
python tests.py
```

Lint
```bash
pip install flake8
flake8
```

&nbsp;

--------

The source code of *rankingbot* is primarily distributed under the terms of
the [GNU Affero General Public License v3.0] or any later version. See
[COPYRIGHT] for details.

[rankingbot]: https://femiwiki.com/w/%EC%82%AC%EC%9A%A9%EC%9E%90:%EB%9E%AD%ED%82%B9%EB%B4%87
[Femiwiki]: https://femiwiki.com
[`(protect)`]: https://femiwiki.com/w/%ED%8A%B9%EC%88%98:%EA%B6%8C%ED%95%9C%EB%B6%80%EC%97%AC%EB%AA%A9%EB%A1%9D#protect
[GNU Affero General Public License v3.0]: LICENSE
[COPYRIGHT]: COPYRIGHT
