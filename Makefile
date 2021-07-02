version=0.1.7

release:
	git tag -a v${version} -m "v${version}"
	git push --tags
