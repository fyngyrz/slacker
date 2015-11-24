# slacker.py readme - BETA

## Overview

Required: [aa\_macro.py](https://github.com/fyngyrz/aa_macro), a webserver
within which you can install this software, and `slacker.py` itself.

`slacker.py` is software that brings the power of the `aa_macro.py`
library to slack's groupware.

The way it works is you type a BOT invocation into a room, which is
private (meaning, no one sees what you type but you) the BOT sends what
you typed off to your webserver, where it is def through `aa_macro.py`,
and then returned to the room publicly in the processed form, identified
as having come from you. For instance, my ID on slack is "fyngyrz", and
the BOT I've set up uses */m* so this is an example of one of the things
I can do:

After I type this: */m The temperature here is {tmp}* 

This text appears: *The temperature here is 32.2F*

`aa_macro` is _extremely_ capable. It can take parameters, parse
them, run system commands, is extensible and can use include files.
For instance, this:

*[style gm Good morning, [b]]*

When invoked this way:

*/m {gm Ben}*

Will produce this in-channel:

*Good morning, Ben*

That's just the proverbial tip of the iceberg. I use aa_macro for
everything from invoking my knowledgebase software to a
script that fetches the local weather conditions from the
national weather service. To learn more, visit my aa_macro
repo and check it out. It's extensively documented, and of
course if you find something needs more explanation, just
me know via the repo and I'll get right on it.

## Setup

### The slack end of things

You'll need two items from slack. The first is a BOT token, and the
second is an incoming WebHook URL. The BOT is used to send what you type
to the script on your server, and the WebHook is used to send the result
back to slack. Both are easily obtained from the "Integrations" menu
option on slack. The token is used to verify that the incoming request
to `slacking.py` on your webserver is actually coming from slack.

Slack will ask what URL the BOT is to invoke. Let's say that you are
using the cgi-bin web structure, so that CGI runs on your server when
invoked like this:

http://yourserver.com/cgi-bin/yourcgi.py

In that case, the URL you provide to slack in requesting the BOT token
will be:

http://yourserver.com/cgi-bin/slacking.py

### On your server

First, you need to go get [aa_macro.py](https://github.com/fyngyrz/aa_macro) -- all
you have to do with it is put `aa_macro.py` in the directory where your
CGI runs. Permissions should be 755 (-rwxr-xr-x)
You don't need anything else from the aa\_macro repo. But you'll want to read the
[aa_macro User's Guide](https://github.com/fyngyrz/aa_macro/blob/master/users-guide.md)
and then keep a link to the
[aa_macro Quick Reference](https://github.com/fyngyrz/aa_macro/blob/master/quickref.md)
handy.

Second, you place `slacking.py` in the same place. Permissions
should be 755 (-rwxr-xr-x) -- You can rename slacking.py if you
like, just be sure to tell slack's BOT what the correct name
is.

Third, you put the slack-cannery.txt file in a place that
is read-write to your webserver user; this is because you
can define macros right from slack, and they are saved in
this file. Make sure the permissions on slack-cannery.txt
are 666 (-rw-rw-rw-)

Fourth, set up the slacker.cfg file with the BOT token, the
WebHook, and the location where slack-cannery.txt will be kept.
`slacker.cfg` goes in the same CGI location as `slacker.py`

That's it. From there on in, things should work.

## Using `slacker.py`

On slack, let's say you set up your BOT to respond to *\m*
(that's what I did... because it's easy to type.) Try
typing:

*/m my reaction is {d}* 

You should see, in the channel that you assigned to the
WebHook:

*my reaction is derp*

There are two ways to add macros to the system. The first can
be done right from slack. Just invoke the bot with the style:

*/m [style pizza I love me some pizza]*

After that, typing */m {pizza}* will emit "I love me some pizza"
in the channel. The style is saved in `slack-cannery.txt` and will
be permanent unless you either replace it with a new definition
(later definitions supercede earlier ones) or delete it from the
file at the server end.

There is one limitation: You can't create a style, or directly use,
`aa_macro`'s *sys*, *embrace*, or *include* operations from within
slack. That's because they would open the door to a significant
security hole on your server where almost anything could be done.
If you want to use these features, you must use the second method.

The second way is by directly editing the `slack-cannery.txt` file at
the server end. You can put anything in there directly, which allows you
to invoke any arbitrary command or script on your server that the web
user has permission to run.

Note that the input text _to_ `slacker.py` is cleansed of backticks,
single and double quotes, the equals sign, and backslashes. These are
replaced with UTF-8 entities (slack uses UTF-8) both for security, and
so that the JSON sent back via the WebHook doesn't break. This limits
what can be sent from the channel in terms of parameters to your
aa_macro commands, but you can convert them back using the macros
themselves if you really think that's a good idea (it isn't, but hey,
it's your server. Perhaps you _like_ security holes.)

## Debugging

If you decide to turn on debugging, `slacker.py` can record various things
to a file called `slacker.txt` in the CGI directory. You'll probably have
to manually create the file and set it's permissions so that it can be
written to, as well as (hopefully temporarily) setting your CGI directory
to be likewise writable. A better choice is to change the file to a
location elsewhere with the correct permissions. I've left it this
way to  keep it simple. I figure if you're going to be debugging, you're
sharp enough to change the file. See the *record\(\)* procedure in
`slacker.py` to make the change.

If you need to debug something, you might consider submitting any
changes you find are required back to the repo so I can improve
`slacker.py`.
