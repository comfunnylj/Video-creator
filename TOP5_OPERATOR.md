# Travel Top5 — Chat-operated runner

This repository includes an **issue-triggered renderer** so an assistant with the connected GitHub app can request a video without asking the user to run shell commands.

## Invocation

Create a GitHub issue in this repository with body:

```text
TOP5_JOB_V1
{
  "mode": "demo",
  "topic": "서울 여행 명소 Top 5 — 작동 확인",
  "places": [
    {
      "name": "남산서울타워",
      "name_en": "N Seoul Tower"
    },
    {
      "name": "경복궁",
      "name_en": "Gyeongbokgung"
    },
    {
      "name": "북촌 한옥마을",
      "name_en": "Bukchon Hanok Village"
    },
    {
      "name": "롯데월드타워",
      "name_en": "Lotte World Tower"
    },
    {
      "name": "반포한강공원",
      "name_en": "Banpo Hangang Park"
    }
  ]
}
```

The GitHub Actions workflow listens for owner-created issues only, renders a 30-second 9:16 video, and uploads an artifact to the run. On success it comments with the run link.

## Modes

- `demo`: renders a **synthetic placeholder**, no real footage. Works without API keys. For runtime verification only.
- `approved_media`: requires each of five places to include `place_verified: true`, plus media with `approved: true`, `license_checked: true`, `source_url`, `credit`, `download_url`. The renderer only downloads from HTTPS *.pexels.com URLs. Review actual place identity, commercial usage rights, and API/provider terms **before** submitting.

This is not a complete travel discovery, copyright verification, affiliation, or auto-posting product. It is the **chat-to-remote-render executor**. No tokens/API keys are committed. GitHub Issue content and artifacts are visible because this repository is public.

## Local test

```bash
python3 top5_operator.py --job sample_job.json --output-dir output
```

Requires Python 3 and ffmpeg (with libass and fonts-nanum).
