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
- When importing a recipe via URL, if the default recipe scraper is unable to read the recipe data from a webpage, the webpage contents will be parsed by OpenAI (:octicons-tag-24: v1.9.0)
- You can import an image of a written recipe, which is sent to OpenAI and imported into Mealie. The recipe can be hand-written or typed, as long as the text is in the picture. You can also optionally have OpenAI translate the recipe into your own language (:octicons-tag-24: v1.12.0)
- You can import a recipe via a video URL (e.g., a YouTube link). The video is transcribed AI, and the transcription is parsed into a recipe (:octicons-tag-24: v3.13.0)
