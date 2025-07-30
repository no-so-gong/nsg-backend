# app/core/config.py

import os
from dotenv import load_dotenv
from pytz import timezone

load_dotenv()

TIMEZONE = os.getenv("TIMEZONE", "Asia/Seoul")
KST = timezone(TIMEZONE)
