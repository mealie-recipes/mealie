# Logs

:octicons-tag-24: v1.5.0

## Highlights

- Logs are written to `/app/data/mealie.log` by default in the container.
- Logs are also written to stdout and stderr.
- You can adjust the log level using the `LOG_LEVEL` environment variable.

## Configuration

Starting in v1.5.0 logging is now highly configurable. Using the `LOG_CONFIG_OVERRIDE` you can provide the application with a custom configuration to log however you'd like. This configuration file is based off the [Python Logging Config](https://docs.python.org/3/library/logging.config.html#logging.config.fileConfig). It can be difficult to understand the configuration at first, so here are some resources to help get started.

- This [YouTube Video](https://www.youtube.com/watch?v=9L77QExPmI0) for a great walkthrough on the logging file format.
- Our [Logging Config](https://github.com/mealie-recipes/mealie/blob/mealie-next/mealie/core/logger/logconf.prod.json).
