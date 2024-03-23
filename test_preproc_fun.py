import preproc_fun
import sys


def test_get_data_aug_params_combinations():
    num_transformation_values = [1, 2, 3]
    num_replacement_values = [1, 2, 3]
    out_of_style_prob_values = [0.0, 0.5, 1.0]

    results = preproc_fun.get_data_aug_params_combinations(num_transformation_values, num_replacement_values, out_of_style_prob_values)
    print(len(results))

    for r in results:
        print(r)

if __name__ == "__main__":
    sys.path.insert(0, "preprocessing")
    test_get_data_aug_params_combinations()