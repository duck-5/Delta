import argparse
import os
from typing import Optional

from smart_delta.src import delta_generator


def create_delta_file(
    filepath_1: str,
    filepath_2: str,
    delta_filepath: str,
    max_diff_length: Optional[int],
    min_length_for_fit: Optional[int],
    base_dir: Optional[str] = None,
):
    if base_dir:
        os.chdir(base_dir)

    with open(filepath_1, "rb") as f:
        data_0 = f.read()
    with open(filepath_2, "rb") as f:
        data_1 = f.read()

    delta_ = delta_generator.DeltaGenerator(
        data_0=data_0,
        data_1=data_1,
        max_diff_length=max_diff_length,
        min_length_for_fit=min_length_for_fit,
    )
    delta_.generate_delta()
    delta_ = bytes(delta_)

    with open(delta_filepath, "wb") as f:
        f.write(delta_)


def main():
    parser = argparse.ArgumentParser(prog="DeltaGenerator")
    parser.add_argument("-b", "--base_file", "--file_1", type=str, required=True)
    parser.add_argument("-f", "--other_file", "--file_2", type=str, required=True)
    parser.add_argument("-d", "--delta_file", type=str, required=True)
    parser.add_argument("-o", "--base_dir", "--dir", type=str)
    parser.add_argument(
        "-m",
        "--max_diff_length",
        help="The delta algorithm tries to find the point where the difference end. "
        "This parameter sets the maximum length the algorithem will search the end of a "
        "difference. Default is 1000.",
        type=int,
    )
    parser.add_argument(
        "-l",
        "--min_length_for_fit",
        help="This parameter sets the minimum length of identical characters to mark ending of "
        "a difference.",
        type=int,
    )
    args = parser.parse_args()

    create_delta_file(
        filepath_1=args.base_file,
        filepath_2=args.other_file,
        delta_filepath=args.delta_file,
        min_length_for_fit=args.min_length_for_fit,
        max_diff_length=args.max_diff_length,
        base_dir=args.base_dir,
    )


if __name__ == "__main__":
    t1 = "Hi my name is yuval"
    t2 = "Hi my name was yuval"
    delta_ = delta_generator.DeltaGenerator(
        data_0=t1,
        data_1=t2,
        max_diff_length=3,
        min_length_for_fit=1,
    )
    elements = delta_.generate_delta()
    print(elements)
    delta_ = bytes(delta_)  # main()
