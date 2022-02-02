from testing.tester import Tester


class BaseResult:
    def initialize(self, t: Tester):
        raise NotImplementedError
