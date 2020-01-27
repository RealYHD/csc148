class Parent:
    """An arbitrary class
    """
    num1: int

    def __init__(self, num1: int) -> None:
        self.num1 = num1


class Child(Parent):
    """A subclass.
    """
    num2: int

    def __init__(self, num1: int, num2: int) -> None:
        self.num2 = num2


if __name__ == '__main__':
    c = Child(1, 2)
    print(c.num2)
    print(c.num1)