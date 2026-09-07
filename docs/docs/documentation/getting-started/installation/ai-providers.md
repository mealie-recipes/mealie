# AI Integration

:octicons-tag-24: v1.7.0

Mealie's AI integration enables several features and enhancements throughout the application. To enable AI features, you must have access to an AI provider (such as OpenAI). Mealie works with any OpenAI-compatible API.

## Configuration

To set up AI providers, visit your group settings.

[Group Settings Demo](https://demo.mealie.io/group){ .md-button .md-button--primary }

- To enable AI features at all, you *must* set a default provider (e.g. `gpt-5`)
- To enable image recognition features, such as creating a recipe from an image, configure a provider capable of image recognition (e.g. `gpt-5`)
- To enable audio transcription features, such as importing a recipe from a video, configure a provider capable of audio transcriptions (e.g. `whisper-1`)

For most users, choosing an OpenAI model (such as `gpt-5`) and supplying the OpenAI API key is all you need to do. Note that while OpenAI has a free tier, it's not sufficiently capable for Mealie (or most other production use cases). For more information, check out [OpenAI's rate limits](https://platform.openai.com/docs/guides/rate-limits). If you deposit $5 into your OpenAI account, you will be permanently bumped up to Tier 1, which is sufficient for Mealie. Cost per-request is dependant on many factors, but Mealie tries to keep token counts conservative.

If you have another provider you'd like to use, such as Azure, you can configure Mealie to use that instead as long as it has an OpenAI-compatible API. For instance, a common self-hosted alternative to OpenAI is [Ollama](https://ollama.com/). To use Ollama with Mealie, set your `base_url` to `http://localhost:11434/v1` (where `http://localhost:11434` is wherever you're hosting Ollama, and `/v1` enables the OpenAI-compatible endpoints). Note that you *must* provide an API key, even though it is ultimately ignored by Ollama.

Note that some models are capable of handling multiple features (e.g. `gpt-5` can handle both normal chat requests and image recognition requests). You may configure one provider for multiple provider features.

While Mealie has prompts for each AI task, you can override these with your own prompts if you'd like. For more information, check out the [backend configuration](../installation/backend-config.md).

## AI Features
- The OpenAI Ingredient Parser can be used as an alternative to the NLP and Brute Force parsers. Simply choose the OpenAI parser while parsing ingredients (:octicons-tag-24: v1.7.0)
- When importing a recipe via URL, if the default recipe scraper is unable to read the recipe data from a webpage, the webpage contents will be parsed by AI (:octicons-tag-24: v1.9.0)
- The **Import with AI** page creates a recipe out of just about anything: pasted text, HTML, or JSON, photos of a recipe, a link, or any combination of them (:octicons-tag-24: v3.23.0)

## Import with AI

The **Import with AI** page, found under *Create ➞ Import with AI*, creates a recipe from any combination of:

- **A URL.** Mealie fetches the page and reads the recipe from it. Give it a link to a video (e.g. YouTube or Instagram) and the video is transcribed instead, provided you've configured an audio provider. The URL is always saved as the recipe's source.
- **Content.** Paste a recipe as plain text, or paste raw HTML or a [schema.org Recipe](https://schema.org/Recipe) JSON object. This is useful when a site blocks Mealie from reading it directly. It's also where you write notes about a recipe you're importing from somewhere else.
- **Images.** Upload one or more photos of a recipe, hand-written or typed. Multiple photos are treated as pages of a single recipe, and the first one becomes the recipe's image. This requires an image provider.

Every source you provide is read, and the results are combined into one description of the recipe. Content you paste alongside a URL, a video, or photos adds to them rather than replacing them, so a page that only partly loaded can be topped up by hand. Where your own content disagrees with the other sources it wins, so it doubles as a place for notes: what to name the recipe, a correction to an ingredient, a step the video skipped over. If content is the only thing you provide, it's simply the recipe's source material.

You can also optionally have the recipe translated into your own language.

### Organizers

Mealie asks AI which tags, categories, and tools the recipe refers to, and always matches what comes back against the organizers you already have, so an import doesn't create a near-duplicate of a tag you're already using.

Organizers that don't match anything you have are discarded, unless you check **Create new organizers**, in which case they're created for you.

Mealie only assigns an organizer that the recipe itself refers to. It won't guess a cuisine from the ingredients or a course from the kind of dish, so a bare list of ingredients and steps usually imports with no organizers at all.

### Which provider is used

Reading the source material is the only step that needs to understand images or audio, so that's the only step that uses your image or audio provider. Turning what it read into a recipe, and working out its organizers, always use your default provider.

This means an import with photos attached is read by your image provider even if you also pasted text alongside them.
