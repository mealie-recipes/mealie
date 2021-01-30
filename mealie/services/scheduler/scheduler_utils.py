import collections

Cron = collections.namedtuple("Cron", "hours minutes")


def cron_parser(time_str: str) -> Cron:
    time = time_str.split(":")
    cron = Cron(hours=int(time[0]), minutes=int(time[1]))

    return cron
