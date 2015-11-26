#!/usr/bin/python

import sys
import cgi
from aa_macro import *

#     Project: slacking.py
#      Author: fyngyrz  (Ben)
#     Contact: fyngyrz@gmail.com (bugs, feature requests, kudos, bitter rejections)
#     Project: slacker.py
#    Homepage: https://github.com/fyngyrz/slacker
#  Depends on: https://github.com/fyngyrz/aa_macro
#     License: None. It's free. *Really* free. Defy invalid social and legal norms.
# Disclaimers: 1) Probably completely broken. Do Not Use. You were explicitly warned. Phbbbbt.
#              2) My code is blackbox, meaning I wrote it without reference to other people's code
#              3) I can't check Other People's Code effectively, so if you use any version
#                 of this that incorporates accepted commits from others, you are then risking
#                 the dangers of OPC, as *well* as risking the use of my code. Using OPC
#                 *also* means you will be using code that may or may not be protected by
#                 copyright, patent, and the like, because our intellectual property system
#                 is pathological. All risks and responsibilities and any subsequent
#                 consequences of this are entirely yours. Have you written your congresscritter
#                 about patent and copyright reform yet?
#  Incep Date: November 24th, 2015
#     LastRev: November 25th, 2015
#  LastDocRev: November 25th, 2015
# Tab spacing: 4 (set your editor to this for sane formatting while reading)
#     Dev Env: Ubuntu 12.04.5 LTS, Python 2.7.3, Apache2
#      Status: BETA
#    Policies:  I will make every effort to never remove functionality or
#               alter existing functionality once past BETA stage. Anything
#               new will be implemented as something new, thus preserving all
#               behavior and API. The only intentional exceptions to this
#               are if a bug is found that does not match the intended behavior,
#               or I determine there is some kind of security risk. What I
#               *will* do is not document older and less capable versions of a
#               function, unless the new functionality is incapable of doing
#               something the older version(s) could do. Remember, this only
#               applies to production code. Until the BETA status is removed,
#               ANYTHING may change. Also, read "Disclaimers", above. Then
#               read it again. Note that while production code as I define it
#               will be more stable, that doesn't imply in any way that it is
#               more, or even at all, reliable. Read "Disclaimers", above. Did
#               I mention you should read the disclaimers? Because you know,
#               you really should. Several times. Read the disclaimers, that is.

# Debug control
# -------------
MODE = 0
if MODE == 0:		# normal operatations
	test = False
	logging = False
elif MODE == 1:		# just log to WWRITE/RECORDER file
	test = False
	logging = True
elif MODE == 2:		# test mode: act like pure slash command
	test = True
	logging = False
elif MODE == 3:		# log to WWRITE/RECORDER and act like pure slash command
	test = True
	logging = True

# Collapse multiple spaces into single spaces
# -------------------------------------------
def crush(t):
	pt = t
	qt = ''
	while pt != qt:
		qt = pt
		pt = qt.replace('  ',' ')
	t = pt.strip()
	return t

# When there are multiple definitions of the same style,
# remove the ones that are older (that is, nearer the
# top of the file.)
# ------------------------------------------------------
cn = '' # set from config file
def cleanup():
	global cn
	try:
		fh = open(cn)
		dat = fh.read()
		fh.close()
		text = 'Style Vocabulary:\n'
		slist = dat.splitlines()
		slist = slist[::-1]
		ict = len(slist)
		tmem = {}
		for line in slist:
			nl = line.split(' ')
			nn = nl[1]
			if tmem.get(nn,'') == '':
				tmem[nn] = line
		fh = open(cn,'w')
		for key in tmem.keys():
			v = tmem[key]+'\n'
			fh.write(tmem[key]+'\n')
		fh.close()
		fct = len(tmem)
		m = 'Cleanup passed: %s in, %s out' % (ict,fct)
	except Exception,e:
		m = 'Cleanup failed: '+str(e)
	return m

# Cleans up text so it is JSON-packaging compatible
# -------------------------------------------------
def textwasher(t):
	kk = 'furshulgenerblinkenlights'
	t = t.replace('\\',kk)
	t = t.replace(kk,'\\\\')
	t = t.replace('\n','\\n')
	t = t.replace("'",'\\u0027')
	t = t.replace('"','\\u0022')
	t = t.replace('`','\\u0060')
	t = t.replace('@','\\u0040')
	t = t.replace('=','\\u003D')
	return t

# Logging
# -------
RECORDER = '' # set from config file
def record(s):
	global RECORDER
	global logging
	if logging == False:
		return
	if s == '':
		s = 'attempt to record an empty string'
	try:
		fh = open(RECORDER,'a')
		fh.write(s+'\n')
		fh.close()
	except:
		pass

# This writes to stdout, which in turn ends up as slash command output
# --------------------------------------------------------------------
def w(t=''):
	if t != '':
		sys.stdout.write(t)
#	sys.stdout.flush() # flushing makes slack say 'OK', undesirable

# This responds to the slash command. At least a content-type header
# is required, or the apache2 webserver will throw an error
# ------------------------------------------------------------------
hdr = 'Content-type: text/plain\n\n'
w(hdr)

# config file reader
# ------------------
def getcfg(file=None):
	ray = {}
	if file == None:
		return ray
	try:
		fh = open(file)
		for line in fh:
			line = line.strip('\n')
			if line != '' and line[0] != '#':
				tag,setting = line.split('=')
				ray[tag] = setting
	except Exception,e:
		print str(e)+' "'+line+'"'
	return ray

# Actually read the config file
# -----------------------------
try:
	c = getcfg('slacker.cfg')

	MODE = int(c['MODE'])

	HOOK = c['HOOK']

	TOKEN = c['TOKEN']

	WWRITE = c['WWRITE']
	if WWRITE[-1:] != '/':
		WWRITE = '%s/' % (WWRITE)

	RECORDER = c['RECORDER']
	RECORDER = '%s%s' % (WWRITE,RECORDER)
except Exception,e:
	t = 'Failed to set config: "%s"' % (str(e))
	w(t)
	raise SystemExit

cn = "%sslack-cannery.txt" % (WWRITE)

# Various ways to call operating system commands and scripts
# subprocess seems to be the best way
# ----------------------------------------------------------
def doit(thing):
	if 0:
		os.system(thing)
	else:
		try:
			subprocess.Popen(thing,shell=True).wait()
		except Exception,e:
			record(str(e))

# Capture information from the slash command's CGI POST
# ------------------------------------------------------
try:
	form = cgi.FieldStorage(keep_blank_values=1)
	token			= form['token'].value
	team_id			= form['team_id'].value
	team_domain		= form['team_domain'].value
	channel_id		= form['channel_id'].value
	channel_name	= form['channel_name'].value
	user_id			= form['user_id'].value
	user_name		= form['user_name'].value
	command			= form['command'].value
	text			= form['text'].value
except:
	if 0:
		user_name='ben'
		text = '{cats}'
		token = TOKEN
	else:
		w('Bad Parameter(s)')
		raise SystemExit

# make sure request at least seems to come from slack slash command
# -----------------------------------------------------------------
if token != TOKEN:
	w('Bad Token')
	raise SystemExit

# Check incoming text for balanced [] and {}
# if unbalanced, we're going to refuse to store
# styles, plus whine about it
# ---------------------------------------------
store = False
lbc = 0
rbc = 0
lsc = 0
rsc = 0
go = False
for c in text:
	if c == '[': lbc += 1
	if c == ']': rbc += 1
	if c == '{': lsc += 1
	if c == '}': rsc += 1
if lbc == rbc and lsc == rsc:
	go = True
else:
	text = 'ERROR: Unbalanced Input'
	w(text)
	raise SystemExit

# detect attempts to store styles from slack
# ------------------------------------------
if len(text) > 7:
	if text[0:7] == "[style ":
		try:
			spos = text.index(' ',7)
		except:
			text = 'ERROR: Malformed Input'
		else:
			store = True

# Prevent use of system level aa_macro features
# ---------------------------------------------
t = text.lower()
badlist = ['[sys ','[include ','[embrace ']
for el in badlist:
	if t.find(el) > -1:
		text = "Sorry, operation(s) not permitted nonlocally"
		w(text)
		raise SystemExit

# store style if that's what needs to be done
# -------------------------------------------
if store == True:
	try:
		fh = open(cn,'a')
		fh.write(text+' \n')
		fh.close()
	except:
		text = 'ERROR: Exception thrown storing style in %s' % (cn)
	else:
		text = 'style "%s" stored.' % (text[7:spos])
		w(text)
		raise SystemExit
else:
	text = '[include %s]%s' % (cn,text)

# grab an instance of aa_macro to use to process text
# ---------------------------------------------------
a = macro()

# Do the text processing
# ----------------------
record('feed to aa_macro: '+text)
record('1')
try:
	text = a.do(text)
except:
	text = 'macro.do() threw an exception. Ooops.'

record('3')

# Can't send unescaped backslashes in a JSON payload,
# and quotes are problematic for curl, so use unicode
# ---------------------------------------------------
record('3a')
if test == False:
	text = textwasher(text)

record('4')
# crush multiple and trailing spaces:
# -----------------------------------
text = crush(text)

# Provide help
# ------------
record('5')
if text == 'help':
	text = 'Help:\n'
	text+= '*cleanup* - eliminates older, unused styles\n'
	text+= '*help* - this message\n'
	text+= '*vocab* - dumps current style vocabulary\n'

# Clean up older versions of macro duplicates
# -------------------------------------------
record('6')
if text == 'cleanup':
	text = cleanup()

# Output list of available macros
# -------------------------------
record('7')
openvocab = not test
record('pre-vocab"%s"' % (text))
if text == 'vocab':
	try:
		fh = open(cn)
		dat = fh.read()
		fh.close()
		text = 'Style Vocabulary:\n'
		slist = dat.splitlines()
		for line in slist:
			if openvocab == True:
				line = textwasher(line)
				line = line.replace('[','\\u005B')
				line = line.replace(']','\\u005D')
				line = line.replace('{','\\u007B')
				line = line.replace('}','\\u007D')
			line += '\n'
			text += line
	except:
		text = 'Unable to open "%s"' % (cn)

# in debug mode, log text now
# ---------------------------
if test == True:
	s = user_name+': '+text.strip()
	record(s)
	w(s)
	raise SystemExit

# Throw result to channel using slack WebHook
# -------------------------------------------
cmd = "curl -X POST --data-urlencode 'payload={\"username\": \"%s\", \"text\": \"%s\"}' %s" % (user_name,text,HOOK)
record(cmd)
doit(cmd)
