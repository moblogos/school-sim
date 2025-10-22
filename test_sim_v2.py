
from simulate_case_v2 import Params, simulate

if __name__ == "__main__":
    p = Params()
    df, extras = simulate(p)
    print(df.head())
