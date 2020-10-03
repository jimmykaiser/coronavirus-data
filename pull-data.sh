# Update this repo
git fetch upstream
git rebase -X theirs upstream/master
# Get latest commit upstream
TODAY=$(git log upstream/master --format=%ad --date=short -n 1 | tr ' ' '-')
# Get hashes of relevant commits from upstream master
today_hash=$(git log upstream/master --pretty=format:"%h" -n 1)
week_ago_hash=$(git log upstream/master --after="`./get_date.py $TODAY 8`" --before="`./get_date.py $TODAY 7`" --pretty=format:"%h" -n 1)
two_week_hash=$(git log upstream/master --after="`./get_date.py $TODAY 15`" --before="`./get_date.py $TODAY 14`" --pretty=format:"%h" -n 1)
# Get data from today
git cat-file -p $today_hash:data-by-modzcta.csv > "data-by-modzcta-today.csv"
# Get data from seven days prior
git cat-file -p $week_ago_hash:data-by-modzcta.csv > "data-by-modzcta-last-week.csv"
# Get data from two weeks prior
git cat-file -p $two_week_hash:data-by-modzcta.csv > "data-by-modzcta-two-weeks-ago.csv"
