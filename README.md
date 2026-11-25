# makefun-news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/sambob0606/makefun-news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/sambob0606/makefun-news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

Sum up 24 November's world news in one image. A pure-stdlib Python program
that draws a newspaper front page as a 1024x1024 PNG: masthead, hero on the
Houthi strike on Riyadh's tallest tower, Gaza / Zaporizhzhia / Estonia,
Senegal / Nvidia / markets, and a footer strip with the rest of the day.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The program writes `out/entry.png` (1024x1024, deterministic: two runs
produce byte-identical files). It needs nothing but Python 3.13's standard
library and no network.

---

<sub>Entered on [make.fun](https://make.fun/?ref=w3shbtmr&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
