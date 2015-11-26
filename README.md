# slacking.py readme - BETA

## Overview

Required:

* [aa\_macro.py](https://github.com/fyngyrz/aa_macro)
* `slacking.py`
* A webserver within which you can install this software

`slacking.py` is software that brings the extensive text manipulation
capabilities of my `aa_macro.py` library to slack's groupware.

The way it works is you type a "Slash Command" invocation into a room,
which is private \(meaning, no one sees what you type but you\) the
slash command sends what you typed off to your webserver without dumping
it in the public channel, where it is fed through `aa_macro.py` by
`slacking.py`, and then returned to the room publicly in the processed
form via a slack WebHook, identified as having come from you.  Here's
the data flow:

SlashCommand **--\> server/slacking.py --\> aa_macro.py --\> WebHook --\>** Channel

For instance, my ID on slack is "fyngyrz", and the slash command I've
set up uses **/m** so this is an example of one of the things I can do:

After I type this: **/m The temperature here is \{tmp\}**

This text appears: **fyngyrz: The temperature here is 32.2F**

`aa_macro` is _extremely_ capable. It can take parameters, parse them,
run system commands, is extensible via external files and can use
include files. For instance, this:

**\[style gm Good morning, \[b\]\]**

When invoked this way:

**/m \{gm Ben\}**

Will produce this in-channel \(of course it won't say "fyngyrz" for you\):

**fyngyrz: Good morning, Ben**

Here are some actual screen captures where I prod my knowledgebase
software right on slack via `aa_macro` and `slacking.py` -- remember
that the **/m** invocations are private so only you see them, while the
responses arrive in the public channel:

![Asking...](http://fyngyrz.com/images/d1.png)  
![...Answer](http://fyngyrz.com/images/d2.png)  
![Further inquiry...](http://fyngyrz.com/images/d3.png)  
![...Answer](http://fyngyrz.com/images/d4.png)  

\(Okay, look, this is *not* the time to critique my KB test mindspace, lol\)

This is the complete `aa_macro` source I use to invoke the knowledgebase:

![macro source](http://fyngyrz.com/images/d5.png)  

Here's what you're looking at: The square brackets define `aa_macro`
primitives. "style" is the primitive that defines a macro. "kb" is the
name of the macro. "sys" is the primitive that runs and captures system
executables. "./aip.py" is the actual command run by "sys". and "[b]" is
the primitive that feeds the content after the macro name into the macro
in that position.

When you invoke a macro you use curly braces: \{mymacro\}

The stdout output of `aip.py` is automatically captured, and returned to
the channel by `slacking.py`. See how easy that was?

There are three built-in commands in `slacking.py`:

Command | Function
------- | --------
**help** | lists these commands  
**vocab** | lists the available macros in `slack-cannery.txt`  
**cleanup** | removes older versions of macros you've re-written  

You use these within slack like this \(assuming you choose M as I did\):

**/m help**

That's just the proverbial tip of the iceberg. You can parse out
individual parameters, process what you get all *kinds* of ways, etc. I
use `aa_macro` for everything from invoking my knowledgebase software to
a script that fetches the local weather conditions from the national
weather service. To learn more, visit my aa_macro repo and check it out.
It's extensively documented, and of course if you find something needs
more explanation, just me know via the repo and I'll get right on it.

## Installation and Setup

### The slack end of things

You'll need two items from slack. Both are easily obtained from the
"Configure Integrations" menu selection on slack within your team space.

#### The Slash Command

The first is a "Slash Command" token. The slash command is used to send
what you type to the script on your server. The token is used to verify
that the incoming request to `slacking.py` on your webserver is actually
coming from slack. You want to set up one of these:

![Slash Command Integration](http://fyngyrz.com/images/ddd9.png)  

Slack will ask what URL the slash command is to invoke. Let's say that
you are using the cgi-bin web structure, so that CGI runs on your server
when invoked like this:

http://yourserver.com/cgi-bin/yourcgi.py

In that case, the URL you provide to slack in requesting the slash command token
will be:

http://yourserver.com/cgi-bin/slacking.py

That's it for the Slash Command setup.

#### The Incoming WebHook

The second thing to configure on slack is an incoming WebHook URL. The
WebHook is used to send the result back to slack. It looks like this:

![Incoming WebHook Integration](http://fyngyrz.com/images/dd2.png)  

When you configure the WebHook, slack will provide you with a URL at slack itself
that begins like this:

**https://hooks.slack.com/services/**...

You simply copy and paste that entire URL, including the portion that goes
where the "..." is in the above fragment, into the configure file where it
says to. That's it for the WebHook setup.

### On your server

First, you need to go get [aa_macro.py](https://github.com/fyngyrz/aa_macro) -- all
you have to do with it is put `aa_macro.py` in the directory where your
CGI runs. Permissions should be 755 \(-rwxr-xr-x\)
You don't need anything else from the aa\_macro repo. But you'll want to read the
[aa_macro User's Guide](https://github.com/fyngyrz/aa_macro/blob/master/users-guide.md)
and then keep a link to that and the 
[aa_macro Quick Reference](https://github.com/fyngyrz/aa_macro/blob/master/quickref.md)
handy. Your webserver must be set up to allow execution of Python scripts in its CGI
configuration. You can rename "aa\_macro.py" and you probably should as a matter of
system security. In that case, however, you'll need to change the associated import
statement in `slacking.py` as well.

Second, you place `slacking.py` in the same place. Permissions on the 
file should be 755 \(-rwxr-xr-x\) -- You can rename slacking.py if you
like, just be sure to tell slack's slash command configurator what the
correct name is.

Third, you put the slack-cannery.txt file in a place that is read-write
to your webserver user; this is because you can define macros right from
slack, and they are saved in this file, which requires a write
operation. Make sure the permissions on slack-cannery.txt are 666
\(-rw-rw-rw-\) Obligatory remark: "Muhaha"

Fourth, set up the slacker.cfg file with the slash command token, the
WebHook, and the location where slack-cannery.txt will be kept according
to the directions within the file. `slacker.cfg` goes in the same CGI
location as `slacking.py`, as it is read-only under normal conditions.

That's it. From there on in, things should work.

## Using `slacking.py`

On slack, let's say you set up your slash command to respond to *\m*
\(that's what I did... because it's easy to type.\) Try
typing:

**/m my reaction is \{d\}**

You should see, in the channel that you assigned to the
WebHook:

**yourusername: my reaction is derp**

There are two ways to add macros to the system.

### Creating Macros on Slack

The first can be done right from slack. Just invoke the slash command
with the style:

**/m \[style pizza I love me some pizza\]**

After that, typing */m \{pizza\}* will emit "I love me some pizza"
in the channel. The style is saved in `slack-cannery.txt` and will
be permanent unless you either replace it with a new definition
\(later definitions supercede earlier ones\) or delete it from the
file at the server end.

There is one limitation: You can't create a style, or directly use,
`aa_macro`'s *sys*, *embrace*, or *include* operations from within
slack. That's because they would open the door to a significant
security hole on your server where almost anything could be done.
If you want to use these features, you must use the second method.

### Creating Macros Directly on the Server

The second way is by directly editing the `slack-cannery.txt` file at
the server end. You can put anything in there directly, which allows you
to invoke any arbitrary command or script on your server that the web
user has permission to run.

_Note:_ **If you use this method, make sure each line with a style
definition ends with two spaces: This tells `aa_macro` to not include
the END-OF-LINE in the output text. The EOL is, technically speaking,
outside of the style definition, so it is treated as something to
reprodude unless the double-space convention is used to prevent it.**

Note that the input text _to_ `slacking.py` is cleansed of backticks,
single and double quotes, the equals sign, and backslashes. These are
replaced with UTF-8 entities \(slack uses UTF-8\) both for security, and
so that the JSON sent back via the WebHook doesn't break. This limits
what can be sent from the channel in terms of parameters to your
aa_macro commands, but you can convert them back using the macros
themselves if you really think that's a good idea \(it isn't, but hey,
it's your server. Perhaps you _like_ security holes.\)

## \(In\)Security

The underlying idea here is that this only intended to run in a slack
room that you and your more-or-less trusted associates are able to
access, and therefore, worries about them trying to actively hack your
server are... less than usual. Contrariwise, it is not advisable to run
this within a slack environment where you have not actively decided to
trust the others present with your server's health, welfare, data,
connectivity, and so on.

There are some provisions in place, such as the inability to define a
macro that calls an OS system function directly from slack \(you'll have
to edit the `slack-cannery.txt` file for that\), some laundering of
various command-line risky characters, and a requirement that the
incoming slash command's token matches the one in the configure file,
but that's not to say that this is by any means bulletproof. If you have
input for me on how to make it more solid, security-wise, than it is, I
will be delighted to pay attention to what you have to say.

## Debugging

If you decide to turn on debugging \(see the options at the top of the
source code\), `slacking.py` can record various things to a file called
`slacking.txt` in the directory set by the WWRITE config variable. There
are four operating modes; normal, logging on, act-as-slash-command, and logging on +
act-as-slash-command.

If find you need to debug something, you might consider submitting any
changes you think are required back to the repo so I can improve
`slacking.py`.
