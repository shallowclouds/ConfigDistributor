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


def filetest(path):
    with open(path, 'rb') as file, Test() as t:
        try:
            print(file.read())
        except:
            return


if __name__ == '__main__':
    filetest('C:/Users/76033/Desktop/'
             'Huffman_Tree.cpp')
