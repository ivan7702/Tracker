#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Copyright 2013, Cong Ding. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http:#www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# author: Cong Ding <dinggnu@gmail.com>
#
# Tracker is a translate helper which helps interpreter track
# the modifications in original documents.
# Currently it only works for Markdown.
#
import sys
import optparse

# Sprcial strings in Markdown
spec = [
	'====', '----',
	'=====', '-----',
	'======', '------',
	'=======', '-------',
	'========', '--------',
	'', '```']

# This function is copied from
# http://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Longest_common_substring
def longest_common_substring(s1, s2):
	m = [[0] * (1 + len(s2)) for i in xrange(1 + len(s1))]
	longest, x_longest = 0, 0
	for x in xrange(1, 1 + len(s1)):
		for y in xrange(1, 1 + len(s2)):
			if s1[x - 1] == s2[y - 1]:
				m[x][y] = m[x - 1][y - 1] + 1
				if m[x][y] > longest:
					longest = m[x][y]
					x_longest = x
			else:
				m[x][y] = 0
	return s1[x_longest - longest: x_longest]

# This function is copied from
# http://rosettacode.org/wiki/Longest_common_subsequence#Dynamic_Programming_6
def longest_common_subsequence(a, b):
	lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
	# row 0 and column 0 are initialized to 0 already
	for i, x in enumerate(a):
		for j, y in enumerate(b):
			if x == y:
				lengths[i+1][j+1] = lengths[i][j] + 1
			else:
				lengths[i+1][j+1] = \
					max(lengths[i+1][j], lengths[i][j+1])
	# read the substring out from the matrix
	result = ""
	x, y = len(a), len(b)
	while x != 0 and y != 0:
		if lengths[x][y] == lengths[x-1][y]:
			x -= 1
		elif lengths[x][y] == lengths[x][y-1]:
			y -= 1
		else:
			assert a[x-1] == b[y-1]
			result = a[x-1] + result
			x -= 1
			y -= 1
	return result

# create a new translation target file
def create(source):

	res = ""
	code = False

	try:
		fr = open(source, 'r')
		slist = fr.readlines()
		fr.close()
	except:
		print 'source file error'
		sys.exit(0)

	# add comments and copy if it is not a special line
	for s in slist:
		s = s[:-1]
		if s[:3] == '```' and  s.find('```') == s.rfind('```'):
			code = not code
		if (s not in spec) and (not code):
			if not(s[:4] == '<!--' and s[-3:] == '-->'):
				res += '<!--' + s + '-->\n'
		res += s + '\n'
	return res

# update an existing translation target file
def update(source, target):

	res = ""

	try:
		fr = open(source, 'r')
		slist = fr.readlines()
		fr.close()
	except:
		print 'source file error'
		sys.exit(0)
	try:
		fr = open(target, 'r')
		tlist = fr.readlines()
		fr.close()
	except:
		return create(source)

	# detect the translation mapping in target file
	code = False
	ti = 0
	trans = {}
	while True:
		if ti >= len(tlist):
			break
		t = tlist[ti][:-1]
		if t[:3] == '```' and  t.find('```') == t.rfind('```'):
			code = not code
		if t[:4] == '<!--' and t[-3:] == '-->' and not code:
			trans[t] = ''
			ti += 1
			while True:
				if ti >= len(tlist):
					break
				s = tlist[ti][:-1]
				if s[:3] == '```' and  s.find('```') == s.rfind('```'):
					code = not code
				if code:
					ti += 1
					break
				if s in spec:
					ti += 1
					break
				if s[:4] == '<!--' and s[-3:] == '-->':
					break
				if trans[t] != '':
					trans[t] += '\n'
				trans[t] += s
				ti += 1
		else:
			ti += 1

	# mapping translation from target file to source file
	code = False
	si = 0
	while True:
		if si >= len(slist):
			break
		s = slist[si][:-1]
		if s[:3] == '```' and  s.find('```') == s.rfind('```'):
			code = not code
		if s not in spec and not code:
			ts = '<!--' + s + '-->'
			# if this line has already been translated
			if ts in trans:
				res += ts + '\n'
				if trans[ts] != '':
					res += trans[ts] + '\n'
			# otherwise we look for the lcs, which might be an old
			# version translation of this line or a closest
			# suggestion
			else:
				ml = 0
				mk = ''
				mv = ''
				mlcs = ''
				for k in trans:
					v = trans[k]
					#lcsl = longest_common_substring(s,k)
					lcsl = longest_common_subsequence(s,k)
					l = len(lcsl)
					if ml < l:
						ml = l
						mk = k
						mv = v
						mlcs = lcsl
				# if the largest len(lcs) of two lines is
				# longer than half of the new line, we treat
				# them as same line but modified
				if len(mlcs) > len(s)/2:
					res += ts + '\n'
					res += '[NEW] ' + s + '\n'
					res += '[ORIGINAL] ' + mk[4:-3] + '\n'
					res += '[TRANSLATION] ' + mv + '\n'
				else:
					res += ts + '\n'
					res += s + '\n'
		else:
			res += s + '\n'
		si += 1
	return res


def main():
	parser = optparse.OptionParser()
	parser.add_option(
			'-w', '', dest='w',
			action='store_true',
			help='write result to target file instead of stdout'
			)
	(opt, args) = parser.parse_args()
	if not args or (opt.w and len(args)!=2) \
			or not(len(args)==1 or len(args)==2):
		print '''
Tracker is a translate helper which helps interpreter track
the modifications in original documents.

Usage: Tracker.py [options] source [target]
Options:
	-w          write result to target file instead of stdout

Examples:
	To create a new translation target, run
		$ python Tracker.py ${source} > ${target}

	To update an existing translation target, run
		$ python Tracker.py ${source} ${target} > ${target}.new
	or run
		$ python Tracker.py -w ${source} ${target}
	to overwrite the ${target} file.
		'''
		sys.exit(1)
	if len(args) == 1:
		source = args[0]
		res = create(source)
		print res
	if len(args) == 2:
		source = args[0]
		target = args[1]
		res = update(source, target)
		if opt.w:
			fw = open(target, 'w')
			fw.write(res)
			fw.close()
		else:
			print res

if __name__ == '__main__':
	main()
