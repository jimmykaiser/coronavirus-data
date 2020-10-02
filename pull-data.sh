# Update repo
git fetch upstream
git rebase -X theirs upstream/master
# Go to latest commit in NYC Health repo
git checkout upstream/master
# Assuming one commit per day...
# Get data from seven days prior
SEVEN_DAYS=$(git log --format=%cr -n 1 HEAD~7 | tr ' ' '-')
git cat-file -p HEAD~7:data-by-modzcta.csv > "data-by-modzcta-$SEVEN_DAYS.csv"
# Get data from two weeks prior
TWO_WEEKS=$(git log --format=%cr -n 1 HEAD~14 | tr ' ' '-')
git cat-file -p HEAD~7:data-by-modzcta.csv > "data-by-modzcta-$TWO_WEEKS.csv"
# Go back to forked repo
git checkout master