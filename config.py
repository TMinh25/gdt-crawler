import os

class Config(object):
        JWT_SECRET = 'FPT-FIS-2023'
        JWT_ALGORITHM = 'HS256'
        JWT_EXP_DELTA_SECONDS = 36000
        MAX_TOTAL_WORKER = 10
        HEADLESS = False
