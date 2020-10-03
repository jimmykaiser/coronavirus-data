#!/usr/bin/env python

import sys
from datetime import datetime, timedelta

def get_date(days_ago):
    """ Get date x days ago """
    date_today = datetime.today()
    days_ago_delta = timedelta(days = days_ago)
    date_wanted = date_today - days_ago_delta
    date_wanted = date_wanted.strftime('%Y-%m-%d')
    print(date_wanted)
    return date_wanted

if __name__ == '__main__':
    get_date(int(sys.argv[1]))
