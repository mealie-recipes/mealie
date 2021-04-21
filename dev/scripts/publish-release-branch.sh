git checkout dev
git merge --strategy=ours master    # keep the content of this branch, but record a merge
git checkout master
git merge dev             # fast-forward master up to the merge


## TODOs

# Create New Branch v0.x.x
# Push Branch Version to Github
# Create Pull Request