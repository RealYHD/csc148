class test1:
    _private: int

    def __init__(self):
        self._private = 1


class test2:
    def __init__(self):
        super().__init__()
        test = test1()
        test1._private = 45
        print(test1._private)

test = test2()