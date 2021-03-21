[rankingbot] [![Github checks status]][github checks link] [![codecov.io status]][codecov.io link]
========
A bot that calculates the rankings of users with high contributions and displays
them on the front page of the [Femiwiki].

You have to grant [`(protect)`] permission to the bot.

&nbsp;

Development
--------
```bash
# Setup venv first
# python -m venv .venv
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install --editable .

# Run
export RANKINGBOT_PASSWORD=xxxxxxxx
python -m rankingbot

# Test
pip install pytest
pytest

# Lint
pip install flake8
flake8

# Packaging
pip install wheel
python setup.py sdist bdist_wheel
```

&nbsp;

--------

The source code of *rankingbot* is primarily distributed under the terms of
the [GNU Affero General Public License v3.0] or any later version. See
[COPYRIGHT] for details.

[rankingbot]: https://femiwiki.com/w/%EC%82%AC%EC%9A%A9%EC%9E%90:%EB%9E%AD%ED%82%B9%EB%B4%87
[github checks status]: https://badgen.net/github/checks/femiwiki/rankingbot
[github checks link]: https://github.com/femiwiki/rankingbot/actions
[codecov.io status]: https://badgen.net/codecov/c/github/femiwiki/rankingbot
[codecov.io link]: https://codecov.io/gh/femiwiki/rankingbot
[Femiwiki]: https://femiwiki.com
[`(protect)`]: https://femiwiki.com/w/%ED%8A%B9%EC%88%98:%EA%B6%8C%ED%95%9C%EB%B6%80%EC%97%AC%EB%AA%A9%EB%A1%9D#protect
[GNU Affero General Public License v3.0]: LICENSE
[COPYRIGHT]: COPYRIGHT
