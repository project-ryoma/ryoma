import pandas as pd
import sys


def load_data(train_data_name):
    try:
        return pd.read_csv(train_data_name)
    except FileNotFoundError:
        print("File not found")
        return None

def test():
    print("test")
    pass

def evaluate():
    pass


# add main with arguments
def entry():
    print(sys.argv[1])
    if sys.argv[1] == "train":
        print(train(sys.argv[2]))
    elif sys.argv[1] == "test":
        test()
    elif sys.argv[1] == "evaluate":
        evaluate()


if __name__ == "__main__":
    # pass arguments to main
    entry()
