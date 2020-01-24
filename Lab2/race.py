class Runner:
    # Attribute types
    name: str
    email: str
    speed: int
    
    def __init__(self, name: str, email: str, speed: int) -> None:
        """
        """
        self.name = name
        self.email = email
        self.speed = speed
    
    def change_speed(new_speed: int) -> None:
        self.speed = new_speed
    
    def change_email(new_email: str) -> None:
        self.email = new_email

class Race:
    # Attribute types
    runners_by_name: dict{str, "Runner"}

    def __init__(self) -> None:
        self.runners_by_name = {}

    def register_runner(self, name: str, email: str, speed: int) -> None:
        """
        """
        if name in self.runners_by_name:
            return
        self.runners_by_name[name] = Runner(name, email, speed)
    
    def withdraw_runner(self, name) -> None:
        """
        """
        del self.runners_by_name[name]

    def runners_by_speed(self, speed: int) -> list[Runner]:
        """
        """
        runners = []
        for runner in self.runners_by_name:
            if runner.speed == speed:
                runners.append(runner)
        return runners
    
    def get_runner(self, name: str) -> list[Runner]:
        """Returns a runner with the given name.
        >>> race = Race()
        >>> race.register_runner("Tom Scott", "tscott@smail.com", 30)
        >>> race.get_runner("Tom Scott")
        """
        runners = []
        for runner in self.runners_by_name:
            if runner.name == name:
                runners.append(runner)
        return runners