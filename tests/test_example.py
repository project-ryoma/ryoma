
from example import load_data, test, evaluate


def test_load_data():
    df = load_data("../data/creditcard.csv")
    assert df.shape == (284807, 31)

    df = load_data("../data/creditcard1.csv")
    assert df is None
