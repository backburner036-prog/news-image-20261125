# news-image-20261125 — Sum up 25 November's world news in one image

[![make.fun bounty](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/backburner036-prog/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/backburner036-prog/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)

One 1024×1024 image summing up Wednesday, 25 November 2026: **35 stories, 7 regions,
UTC timeline** — hero: Asia tumbles as the AI rally reverses (Kospi −5.3%, Nikkei −2.9%,
Reuters intraday); leads: US tariffs on China/EU, CIA–ODNI cyber breach, China rocket
carrying a Pakistani astronaut.

## Build

```bash
python3 render.py   # writes entry.png (deterministic, byte-identical across runs)
node main.ts        # verifies entry.png (PNG 1024×1024, ≤1 MiB) and copies it to $MAKEFUN_OUTPUT_DIR
```

## Files

- `render.py` — Pillow renderer (standard library + Pillow, no network)
- `main.ts` — Node 22 entrypoint (verify + copy to output dir)
- `entry.png` — the submission image, 1024×1024
