class Typed(object):
    _expected_type = type(None)

    def __set_name__(self, owner, name):
        self.name = name
    # def __init__(self, name=None):
        # self.name = name

    def __set__(self, instance, value):
        if not isinstance(value, self._expected_type):
            raise TypeError('Expected' + str(self._expected_type))
        instance.__dict__[self.name] = value


class String(Typed):
    _expected_type = str


class FourDigitstr(String):
    def __set__(self, instance, value):
        if len(value) != 4:
            raise TypeError(f'Expected 4 digit len but receive result {value}')
        try:
            int(value)
        except:
            raise TypeError(f'Expected integer form but receive result {value}')
        super().__set__(instance, value)


if __name__ == '__main__':

    class Test:
        code = FourDigitstr()

        def __init__(self, code):
            self.code = code

test1 = Test('1234')
# test2 = Test('abcd')
# test3 = Test('123')

