from io import StringIO


class RedirectedInputStream:
    """
    Mock for testing. If get_username or get_password is requested will raise
    an exception except we have a value to return.
    """

    def __init__(self, answers: list):
        self.answers = answers

    def readline(self):
        if not self.answers:
            raise Exception(
                "\n\n**********\n\nClass MockedInputStream: "
                "There are no more inputs to be returned.\n"
                "CHECK THE 'inputs=[]' ARGUMENT OF THE TESTCLIENT\n**********+*\n\n\n"
            )
        ret = self.answers.pop(0)
        return ret


class RedirectedTestOutput(StringIO):
    def __init__(self):
        # Chage to super() for Py3
        StringIO.__init__(self)

    def clear(self):
        self.seek(0)
        self.truncate(0)

    def __repr__(self):
        return self.getvalue()

    def __str__(self, *args, **kwargs):
        return self.__repr__()

    def __eq__(self, value):
        return self.__repr__() == value

    def __contains__(self, value):
        return value in self.__repr__()
