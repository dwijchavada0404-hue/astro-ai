# Temporary feature patch scripts may use pathlib to update large files.
# CI executes only `.github/feature_patch.py` on same-repository pull requests.
# The live patch file is deleted automatically before the generated changes
# are committed, so feature patches do not remain in merged code.
