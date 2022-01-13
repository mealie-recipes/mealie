import time


# log_lifetime is a class decorator that logs the creation and destruction of a class
# It is used to track the lifespan of a class during development or testing.
# It SHOULD NOT be used in production code.
def log_lifetime(cls):
    class LifeTimeClass(cls):
        def __init__(self, *args, **kwargs):
            print(f"Creating an instance of {cls.__name__}")  # noqa: T001
            self.__lifespan_timer_start = time.perf_counter()

            super().__init__(*args, **kwargs)

        def __del__(self):
            toc = time.perf_counter()
            print(f"Downloaded the tutorial in {toc - self.__lifespan_timer_start:0.4f} seconds")  # noqa: T001

            print(f"Deleting an instance of {cls.__name__}")  # noqa: T001

            try:
                super().__del__()
            except AttributeError:
                pass

    return LifeTimeClass
