Tracker
=======

Tracker is a translate helper which helps interpreter track the modifications in original documents.

Currently it only works for Markdown.

##### Usage: Tracker.py [options] source [target]

###### Options:
	-w          write result to target file instead of stdout

###### Examples:
	To create a new translation target, run
		$ python Tracker.py ${source} > ${target}

	To update an existing translation target, run
		$ python Tracker.py ${source} ${target} > ${target}.new
	or run
		$ python Tracker.py -w ${source} ${target}
	to overwrite the ${target} file.
