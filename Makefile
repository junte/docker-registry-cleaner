version=0.1.3

release:
	git tag -a v${version} -m "v${version}"
	git push --tags
