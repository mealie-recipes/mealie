# Using iOS Shortcuts with Mealie

!!! info
    This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!

![Image from apple site](https://help.apple.com/assets/5E8CEA35094622DF10489984/5E8CEA42094622DF1048998D/en_US/ed1f9c157cdefc13e0161e0f70015455.png)

User [brasilikum](https://github.com/brasilikum) opened an issue on the main repo about how they had created an [iOS shortcut](https://github.com/hay-kot/mealie/issues/103) for interested users. This is a useful utility for iOS users who browse for recipes in their web browser from their devices. Recent updates to Mealie has made this original shortcut break. Reddit user [BooNooBooNooB](https://www.reddit.com/user/BooNooBooNooB/) has helped to create a new working version.

Don't know what an iOS shortcut is? Neither did I! Experienced iOS users may already be familiar with this utility but for the uninitiated, here is the official Apple explanation:

> A shortcut is a quick way to get one or more tasks done with your apps. The Shortcuts app lets you create your own shortcuts with multiple steps. For example, build a “Surf Time” shortcut that grabs the surf report, gives an ETA to the beach, and launches your surf music playlist.

Basically it is a visual scripting language that lets a user build an automation in a guided fashion. The automation can be [shared with anyone](https://www.icloud.com/shortcuts/4c40fcc6f39549f9a189995a449cd44f) but if it is a user creation, you'll have to jump through a few hoops to make an untrusted automation work on your device.

You need to replace `username` and `password` with the login information for your mealie instance.

![screenshot](../img/iOS_username.jpg)

Then, you need to put in your mealie domain. The API port of `:9000` is not needed when putting your domain in the text field.

![screenshot](../img/iOS_host.jpg)

You should now be able to share a website to the shortcut and have mealie grab all the necessary information!
