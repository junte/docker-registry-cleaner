version=0.1.5

release:
	git tag -a v${version} -m "v${version}"
	git push --tags
