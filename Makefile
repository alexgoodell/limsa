

SHELL = /usr/local/bin/fish

backup:
	git add . -A
	git commit -m "Update"
	git push origin master