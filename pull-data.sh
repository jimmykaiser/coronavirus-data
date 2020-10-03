# Get hashes of relevant commits from upstream master
today_hash=$(git log upstream/master --after="`./get_date.py 1`" --before="`./get_date.py 0`" --pretty=format:"%h" -n 1)
week_ago_hash=$(git log upstream/master --after="`./get_date.py 8`" --before="`./get_date.py 7`" --pretty=format:"%h" -n 1)
two_week_hash=$(git log upstream/master --after="`./get_date.py 15`" --before="`./get_date.py 14`" --pretty=format:"%h" -n 1)
# Get data from today
TODAY=$(git log $today_hash --format=%ad --date=short -n 1 | tr ' ' '-')
git cat-file -p $today_hash:data-by-modzcta.csv > "data-by-modzcta-$TODAY.csv"
# Get data from seven days prior
SEVEN_DAYS=$(git log $week_ago_hash --format=%ad --date=short -n 1 | tr ' ' '-')
git cat-file -p $week_ago_hash:data-by-modzcta.csv > "data-by-modzcta-$SEVEN_DAYS.csv"
# Get data from two weeks prior
TWO_WEEKS=$(git log $two_week_hash --format=%ad --date=short -n 1 | tr ' ' '-')
git cat-file -p $two_week_hash:data-by-modzcta.csv > "data-by-modzcta-$TWO_WEEKS.csv"
