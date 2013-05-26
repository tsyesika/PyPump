Hacking
=======
If you're wanting to work on PyPump. Please read this first, if you've got a problem with any of it let me know rather than just ignoring it, if you've got a good reason we can change it. Main thing is we all work the same way to reduce the chance of problems occuring.


Branches
--------
If you're working on the main repo then please create a branch name which looks like

JT-13-NewObjects

where
JT = your initials (JT = Jessica Tallon)
13 = issue number 13 (this must refer to a github issue, if there isn't an issue make one first.)
NewObjects = a very short description, in this case this is the new objects we're creating (Person, Location, Image, etc)


Code Style
----------
- Functions/methods should have descriptive names with doc strings
- Files should have the GPL v3 licence at the top (if other code is used licence must be compatable and clearly stated the source and origionating authors (prefrably the commit hash too (if using git))
- Try not to go over 80 chars across (in accordance to PEP-8), currently we do in places, this will be changed soon.
- Currently unit tests are non-existant we're soon going to cover PyPump with them, please keep this in mind
- 4 spaces not tabulars or any other kind of spaces 

Documentation
-------------
Documentation is welcome in any language but english is needed too. If you're writing code which the user of PyPump may be using make sure you have written docs to cover it. If you're not sure how please go to #pypump on MegNet irc network (http://megworld.co.uk)


Git commits
-----------
Try not to make one large commit at the end with all your code in, make small commits which contain small specific bits of code with descriptive commit messages (often useful to add #<issue number> as it automatically documents it in the issue tracker). 

Tip:
`
$ git add -p
`

Will show you blocks of code, this will help you split your commits out to specific things (NB: git add -p does not look for new files you've added, ensure you do git add <new file> for that)
