# Update repo
git fetch upstream
git rebase -X theirs upstream/master
# Get data from seven days prior
git checkout upstream/master
git cat-file -p HEAD~7:data-by-modzcta.csv > data-by-modzcta-last-week.csv