0.7
===
- Added Audio and Video objects
- Work around bug in pump.io favorites feed which only let us get 20 latest items (https://github.com/xray7224/PyPump/issues/65)
- Person.update() now updates Person.location
- Fixed bug where PyPump with Python3 failed to save credentials to theJSONStore

0.6
===
- Person no longer accept a webfinger without a hostname
- PumpObject.add_link and .add_links renamed to ._add_link and ._add_links
- Recipients can now be set for Comment, Person objects
- Recipient properties (.to, .cc, .bto, .bcc) has been moved from Activity to Activity.obj
- Feeds (inbox, followers, etc) can now be sliced by object or object_id.
- Feed.items(offset=int|since=id|before=id, limit=20) method.
- Unicode improvements when printing Pump objects.
- Instead of skipping an Object attribute which has no response data (f.ex Note.deleted when note has not been deleted) we now set the attribute to None.
- Fixed WebPump OAuth token issue (#89)
- Allow you to use \<commentable object\>.comment() by passing in just a string apposed to a Comment object. ([44f3426](https://github.com/xray7224/PyPump/commit/44f34268a4d0f97107438baf05510b75f9fdebee))
- Introduce "Store" object for saving persistant data.

Earlier Releases
================

Sorry we didn't keep a change log prior to 0.6, you'll have to fish through the git commits to see what's changed.
