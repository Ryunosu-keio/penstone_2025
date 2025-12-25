import itertools

def generate_combinations():
    param_options = ["g", "c", "s", "b", "e"]
    param_values = [0, 1, 2]

    # パラメータの組み合わせを生成
    param_combinations = itertools.combinations(param_options, 3)

    # 各組み合わせに対して0, 1, 2の値の組み合わせを生成
    for combination in param_combinations:
        for value_combination in itertools.product(param_values, repeat=3):
            yield combination, value_combination

if __name__ == "__main__":
    for combo in generate_combinations():
        print(combo)