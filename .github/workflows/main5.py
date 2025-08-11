name: signal-bot-12
on:
  schedule:
    - cron: '0 12 * * *' # 12:00 UTC
  workflow_dispatch: {}

jobs:
  run-bot:
    runs-on: ubuntu-latest
    timeout-minutes: 180
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install telethon requests
      - name: Run signal bot
        run: python main.py
