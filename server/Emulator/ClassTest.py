import sys
import traceback


class Test:
    def __init__(self):
        self.a = 10

    def __enter__(self):
        return self
        # raise ZeroDivisionError

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('Exception!!!:\n', exc_type, exc_val)

    def raise_exp(self):
        raise Exception('Test Exception').with_traceback(sys.exc_info()[2])

    def __str__(self):
        return '___str__() is called'


def filetest(path):
    with open(path, 'rb') as file, Test() as t:
        try:
            t.raise_exp()
        except Exception as e:
            traceback.print_exception(type(e), e, e.__traceback__)


if __name__ == '__main__':
    # filetest('C:/Users/76033/Desktop/'
    #          'Huffman_Tree.cpp')
    pass
