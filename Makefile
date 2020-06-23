version=0.1.4

release:
	git tag -a v${version} -m "v${version}"
	git push --tags
