class Test:
    def __init__(self):
        self.a = 10

    def __enter__(self):
        return self
        # raise ZeroDivisionError

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Exception!!!:\n', exc_type, exc_val)

    def raise_exp(self):
        raise ConnectionRefusedError


if __name__ == '__main__':
    with Test() as t:
        print('...')
        t.raise_exp()

    print(',..sadf.sdaf.')
