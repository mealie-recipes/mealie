class NotSet:
    def __bool__(self):
        return False


NOT_SET = NotSet()
