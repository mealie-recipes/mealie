# Using iOS Shortcuts with Mealie
![](/img/iphone-image.png){: align=right style="height:400px;width:400px"}


User  [brasilikum](https://github.com/brasilikum) opened an issue on the main repo about how they had created an [iOS shortcut](https://github.com/hay-kot/mealie/issues/103) for interested users. This is a useful utility for iOS users who browse for recipes in their web browser from their devices.

Don't know what an iOS shortcut is? Neither did I! Experienced iOS users may already be familiar with this utility but for the uninitiated, here is the official Apple explanation:


> A shortcut is a quick way to get one or more tasks done with your apps. The Shortcuts app lets you create your own shortcuts with multiple steps. For example, build a “Surf Time” shortcut that grabs the surf report, gives an ETA to the beach, and launches your surf music playlist.


Basically it is a visual scripting language that lets a user build an automation in a guided fashion. The automation can be [shared with anyone](https://www.icloud.com/shortcuts/6ae356d5fc644cfa8983a3c90f242fbb) but if it is a user creation, you'll have to jump through a few hoops to make an untrusted automation work on your device. In brasilikum's shortcut, you need to make changes for it to work. Recent updates to the project have changed some of the syntax and folder structure since its original creation.


![screenshot](/img/ios-shortcut-image.jpg){: align=right style="height:500;width:400px"}



!!! tip
    You may need to change the url depending on which version you're using. Recipe is now plural and there is no trailing "/" at the end of the string.
    
    ```
    api/recipe/create-url/
    ```

    to

    ```
    api/recipes/create-url
    ```

    

Having made those changes, you should now be able to share a website to the shortcut and have mealie grab all the necessary information!
