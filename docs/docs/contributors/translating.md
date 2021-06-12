# Contributing with Translations
Translations can be a great way **for non-coders** to contribute to project.
We use **[Crowdin](https://crowdin.com/project/mealie){:target="_blank"}** to allow several contributors to work on translating Mealie. 
You can simply help by voting for your preferred translations, or even by completely translating Mealie into a new language.

Translations are regularly pulled from Crowdin and included in each new release.

Please use Crowdin as much as possible if you have any question/issue regarding a particular string. You can take a look at [Crowdin Knowledge base](https://support.crowdin.com/for-volunteer-translators/){:target="_blank"} if you want to know more about how to use this tool.

## My language is missing in Mealie
Once your language is translated on Crowdin, we need to manually add it in Mealie. If you believe your language is ready for use, please create an issue on GitHub. 

## I can't find a particular text in Crowdin
There can be several reasons:
- The text you're looking for is outdated: someone has already changed it or it will be removed/changed in the next release.
- It is possible some texts are not translatable (yet) for technical reasons. If you spot one, please reach out to us on [Discord](https://discord.gg/QuStdQGSGK){:target="_blank"} or raise an issue on GitHub.

## Technical information
We use vue-i18n package for internationalization. Translations are stored in json format located in [frontend/src/locales/messages](https://github.com/hay-kot/mealie/tree/master/frontend/src/locales/messages){:target="_blank"}.

[i18n Ally for VScode](https://marketplace.visualstudio.com/items?itemName=lokalise.i18n-ally){:target="_blank"} is helpful for generating new strings to translate. It also has a nice feature, which shows translations in-place when editing code.