# Feature patch hook

For same-repository pull requests only, CI may execute a temporary `.github/feature_patch.py` script before tests. The script is removed and any generated source changes are committed back to the feature branch automatically. This supports phone-first development of large integration files while keeping all generated changes covered by the full pytest suite.
