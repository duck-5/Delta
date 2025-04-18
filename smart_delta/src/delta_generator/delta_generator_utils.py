import itertools
from typing import Optional

from smart_delta.src import (
    INSERTION_MARK,
    DELETION_MARK,
    REPLACEMENT_MARK,
)

from smart_delta.src.delta_utils import range_diff
from smart_delta.src.delta_element import DeltaElement


def generate_opt_delta(
    data_0: str, data_1: str, max_diff_length: int, min_length_for_fit: int
):
    print(f"entered with {min_length_for_fit=}, {data_0=}, {data_1=}")
    diff_beginning_index_0 = None
    delta_elements = []

    index_0, index_1 = 0, 0

    while index_0 < len(data_0) and index_1 < len(data_1):
        if data_0[index_0] != data_1[index_1]:
            print("entered if")
            diff_beginning_index_0 = index_0
            diff_beginning_index_1 = index_1

            options = []
            for min_length_for_fit in range(3, 10):
                elements = []
                diff_beginning_index_0 = index_0
                diff_beginning_index_1 = index_1

                diff_ending_0, diff_ending_1 = range_diff(
                    data_0=data_0[diff_beginning_index_0:],
                    data_1=data_1[diff_beginning_index_1:],
                    max_diff_length=max_diff_length,
                    min_length_for_fit=min_length_for_fit,
                )

                diff_ending_0 += diff_beginning_index_0
                diff_ending_1 += diff_beginning_index_1

            
                
                delta_element = create_delta_element(
                    data_0,
                    data_1,
                    diff_beginning_index_0,
                    diff_ending_0,
                    diff_beginning_index_1,
                    diff_ending_1,
                )
                if delta_element is not None:
                   elements.append(delta_element)

                print(diff_ending_0, diff_ending_1, len(data_0), len(data_1))
                if diff_ending_0 == len(data_0) or diff_ending_1 == len(data_1):
                    return elements
                
                n_opt = []
                for n_min_length_for_fit in range(3, 10):
                    print(f"searching generations... {n_min_length_for_fit=}")
                    n_opt.append(
                        generate_opt_delta(
                            data_0=data_0[diff_ending_0:],
                            data_1=data_1[diff_ending_1:],
                            max_diff_length=1000,
                            min_length_for_fit=n_min_length_for_fit,
                        )
                    )
                sizes = [sum([len(ele) for ele in elems]) for elems in n_opt]
                # print(sizes)
                best_index = sizes.index(min(sizes))
                elements += n_opt[best_index]

                options.append(elements)

            sizes = [sum([len(ele) for ele in elems]) for elems in options]
            # print(options)
            best_index = sizes.index(min(sizes))
            delta_elements = options[best_index]
            print("EXITED!")
            return delta_elements

            index_0 = diff_ending_0 - 1
            index_1 = diff_ending_1 - 1

            diff_beginning_index_0 = None
            break

        index_0 += 1
        index_1 += 1
    if not diff_beginning_index_0:
        diff_beginning_index_0 = index_0
        diff_beginning_index_1 = index_1

    if index_0 < len(data_0) and index_1 >= len(data_1):
        delta_elements.append(
            DeltaElement(
                DELETION_MARK,
                diff_beginning_index_1,
                data_0[diff_beginning_index_0:],
            )
        )

    if index_1 < len(data_1) and index_0 >= len(data_0):
        delta_elements.append(
            DeltaElement(
                INSERTION_MARK,
                diff_beginning_index_1,
                data_1[diff_beginning_index_1:],
            )
        )
    return delta_elements


def generate_delta(
    data_0: str, data_1: str, max_diff_length: int, min_length_for_fit: int
):
    diff_beginning_index_0 = None
    delta_elements = []

    index_0, index_1 = 0, 0

    while index_0 < len(data_0) and index_1 < len(data_1):
        if data_0[index_0] != data_1[index_1]:
            diff_beginning_index_0 = index_0
            diff_beginning_index_1 = index_1
            diff_ending_0, diff_ending_1 = range_diff(
                data_0=data_0[diff_beginning_index_0:],
                data_1=data_1[diff_beginning_index_1:],
                max_diff_length=max_diff_length,
                min_length_for_fit=min_length_for_fit,
            )
            diff_ending_0 += diff_beginning_index_0
            diff_ending_1 += diff_beginning_index_1

            delta_element = create_delta_element(
                data_0,
                data_1,
                diff_beginning_index_0,
                diff_ending_0,
                diff_beginning_index_1,
                diff_ending_1,
            )
            if delta_element is not None:
                delta_elements.append(delta_element)

            index_0 = diff_ending_0 - 1
            index_1 = diff_ending_1 - 1

            diff_beginning_index_0 = None

        index_0 += 1
        index_1 += 1
    if not diff_beginning_index_0:
        diff_beginning_index_0 = index_0
        diff_beginning_index_1 = index_1

    if index_0 < len(data_0) and index_1 >= len(data_1):
        delta_elements.append(
            DeltaElement(
                DELETION_MARK,
                diff_beginning_index_1,
                data_0[diff_beginning_index_0:],
            )
        )

    if index_1 < len(data_1) and index_0 >= len(data_0):
        delta_elements.append(
            DeltaElement(
                INSERTION_MARK,
                diff_beginning_index_1,
                data_1[diff_beginning_index_1:],
            )
        )
    return delta_elements


def create_delta_element(
    data_0: str,
    data_1: str,
    diff_beginning_index_0: int,
    diff_ending_0: int,
    diff_beginning_index_1: int,
    diff_ending_1: int,
) -> Optional[DeltaElement]:
    if (
        diff_ending_0 != diff_beginning_index_0
        and diff_ending_1 == diff_beginning_index_1
    ):
        return DeltaElement(
            DELETION_MARK,
            diff_beginning_index_1,
            data_0[diff_beginning_index_0:diff_ending_0],
        )

    if (
        diff_ending_1 != diff_beginning_index_1
        and diff_ending_0 == diff_beginning_index_0
    ):
        return DeltaElement(
            INSERTION_MARK,
            diff_beginning_index_1,
            data_1[diff_beginning_index_1:diff_ending_1],
        )

    if (
        diff_ending_0 != diff_beginning_index_0
        and diff_ending_1 != diff_beginning_index_1
    ):
        return DeltaElement(
            REPLACEMENT_MARK,
            diff_beginning_index_1,
            data_0[diff_beginning_index_0:diff_ending_0],
            data_1[diff_beginning_index_1:diff_ending_1],
        )


text_1 = b"""
Hi. My name is yuval and I like cookies. I like cookies because a lot of reasons.
"""

text_2 = b"""
Hi. My name is yuval and I like cookies because I like cookies because a lot of reasons. a lot of reasons.
"""
res = generate_opt_delta(text_1, text_2, 1000, 1000)
print("Res:")
print(res)
