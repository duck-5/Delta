from struct import unpack
from typing import Tuple, Iterable, List, Callable, Union

from smart_delta.src import (
    UNMARK_MARK,
    REPLACEMENT_SPLIT_MARK,
)


def print_data(data: str) -> None:
    print(" ".join([str(i) for i in range(len(data))]))
    print("".join([data[i] + " " * len(str(i)) for i in range(len(data))]))


def find_system_marks(bytes_string: bytes, marks: Iterable[str]) -> List[str]:
    indices = []
    is_after_mark = False

    for i, char in enumerate(unpack(f"{len(bytes_string)}c", bytes_string)):
        if char == UNMARK_MARK:
            if is_after_mark:
                is_after_mark = False
            else:
                is_after_mark = True

        if char != UNMARK_MARK and is_after_mark:
            is_after_mark = False

        elif char in marks and not is_after_mark:
            indices.append(i)
    return indices


def split_payload(payload: bytes) -> Tuple[bytes, bytes]:
    split_index = find_system_marks(payload, (REPLACEMENT_SPLIT_MARK,))[0]
    return payload[:split_index], payload[split_index + 1 :]


def replace_signs(data: Union[str, bytes], to_replace: Union[str, bytes], replace_with: Union[str, bytes]) -> Union[str, bytes]:
    is_after_mark = False
    new_data = data
    for index, char in enumerate(data):
        if data[index : index + len(to_replace)] == to_replace and not is_after_mark:
            new_data = (
                new_data[: index + len(new_data) - len(data)]
                + replace_with
                + data[index + len(to_replace) :]
            )
        elif char == UNMARK_MARK:
            if is_after_mark:
                is_after_mark = False
            else:
                is_after_mark = True
        elif is_after_mark:
            is_after_mark = False
    return new_data

def range_diff(
    data_0: bytes, data_1: bytes, max_diff_length: int, min_length_for_fit
) -> Tuple[int, int]:
    index_0_for_0, index_1_for_0 = 0, 0
    index_0_for_1, index_1_for_1 = 0, 0
    
    len_data_0 = len(data_0)
    len_data_1 = len(data_1)

    check_if_fit_found: Callable[
        [bytes, bytes, int, int], bool
    ] = lambda index_0, index_1: (
        data_0[index_0:index_0 + min_length_for_fit] == data_1[index_1:index_1 + min_length_for_fit]
    )

    while index_0_for_0 < len_data_0 and index_1_for_1 < len_data_1:
        while True:
            if not (index_1_for_0 < max_diff_length and index_1_for_0 < len_data_1) and not (index_0_for_1 < max_diff_length and index_0_for_1 < len_data_0):
                break

            if check_if_fit_found(index_0_for_0, index_1_for_0):
                return index_0_for_0, index_1_for_0

            if check_if_fit_found(index_0_for_1, index_1_for_1):
                return index_0_for_1, index_1_for_1

            index_1_for_0 += 1
            index_0_for_1 += 1

        index_0_for_0 += 1
        index_1_for_0 = 0
        index_0_for_1 = 0
        index_1_for_1 += 1
    return len_data_0, len_data_1
