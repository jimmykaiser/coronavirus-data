# Update this repo
git fetch upstream
git rebase -X theirs upstream/master > rebase_log.txt
# Get latest commit upstream
TODAY=$(git log upstream/master --format=%ad --date=short -n 1 | tr ' ' '-')
echo "Latest commit is $TODAY"
# Get hashes of relevant commits from upstream master
today_hash=$(git log upstream/master --pretty=format:"%h" -n 1)
week_ago_hash=$(git log upstream/master --after="`./get_date.py $TODAY 8`" --before="`./get_date.py $TODAY 7`" --pretty=format:"%h" -n 1)
two_week_hash=$(git log upstream/master --after="`./get_date.py $TODAY 15`" --before="`./get_date.py $TODAY 14`" --pretty=format:"%h" -n 1)
# Get data from today
git cat-file -p $today_hash:totals/data-by-modzcta.csv > "data-by-modzcta-today.csv"
echo "Got data as of $TODAY"
# Get data from seven days prior
git cat-file -p $week_ago_hash:data-by-modzcta.csv > "data-by-modzcta-last-week.csv"
WEEK_AGO=$(git log $week_ago_hash --format=%ad --date=short -n 1 | tr ' ' '-')
echo "Got data as of $WEEK_AGO"
# Get data from two weeks prior
git cat-file -p $two_week_hash:data-by-modzcta.csv > "data-by-modzcta-two-weeks-ago.csv"
TWO_WEEKS=$(git log $two_week_hash --format=%ad --date=short -n 1 | tr ' ' '-')
echo "Got data as of $TWO_WEEKS"
# Make new version of map
python make_map.py $TODAY