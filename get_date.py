#!/usr/bin/env python

import sys
from datetime import datetime, timedelta

def get_date(ref_date, days_ago):
    """ 
    Get date x days ago from reference date
    ref_date: string in format yyyy-mm-dd
    days_ago: int
    """
    ref_date = datetime.strptime(ref_date, '%Y-%m-%d')
    days_ago_delta = timedelta(days = days_ago)
    date_wanted = ref_date - days_ago_delta
    date_wanted = date_wanted.strftime('%Y-%m-%d')
    print(date_wanted)
    return date_wanted

if __name__ == '__main__':
    get_date(sys.argv[1], int(sys.argv[2]))
