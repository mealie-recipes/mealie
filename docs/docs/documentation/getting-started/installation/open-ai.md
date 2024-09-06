# OpenAI Integration

:octicons-tag-24: v1.7.0

Mealie's OpenAI integration enables several features and enhancements throughout the application. To enable OpenAI features, you must have an account with OpenAI and configure Mealie to use the OpenAI API key (for more information, check out the [backend configuration](./backend-config.md#openai)).

## Configuration

For most users, supplying the OpenAI API key is all you need to do; you will use the regular OpenAI service with the default language model. Note that while OpenAI has a free tier, it's not sufficiently capable for Mealie (or most other production use cases). For more information, check out [OpenAI's rate limits](https://platform.openai.com/docs/guides/rate-limits). If you deposit $5 into your OpenAI account, you will be permanently bumped up to Tier 1, which is sufficient for Mealie. Cost per-request is dependant on many factors, but Mealie tries to keep token counts conservative.

Alternatively, if you have another service you'd like to use in-place of OpenAI, you can configure Mealie to use that instead, as long as it has an OpenAI-compatible API. For instance, a common self-hosted alternative to OpenAI is [Ollama](https://ollama.com/). To use Ollama with Mealie, change your `OPENAI_BASE_URL` to `http://localhost:11434/v1` (where `http://localhost:11434` is wherever you're hosting Ollama, and `/v1` enables the OpenAI-compatible endpoints). Note that you *must* provide an API key, even though it is ultimately ignored by Ollama.

If you wish to disable image recognition features (to save costs, or because your custom model doesn't support them) you can set `OPENAI_ENABLE_IMAGE_SERVICES` to `False`. For more information on what configuration options are available, check out the [backend configuration](./backend-config.md#openai).

## OpenAI Features
- The OpenAI Ingredient Parser can be used as an alternative to the NLP and Brute Force parsers. Simply choose the OpenAI parser while parsing ingredients (:octicons-tag-24: v1.7.0)
- When importing a recipe via URL, if the default recipe scraper is unable to read the recipe data from a webpage, the webpage contents will be parsed by OpenAI (:octicons-tag-24: v1.9.0)
- You can import an image of a written recipe, which is sent to OpenAI and imported into Mealie. The recipe can be hand-written or typed, as long as the text is in the picture. You can also optionally have OpenAI translate the recipe into your own language (:octicons-tag-24: v1.12.0)
