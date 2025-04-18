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


def replace_signs(
    data: Union[str, bytes],
    to_replace: Union[str, bytes],
    replace_with: Union[str, bytes],
) -> Union[str, bytes]:
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


def range_fit(data_0: bytes, data_1: bytes) -> int:
    for i in range(min(len(data_0), len(data_1))):
        if data_0[i] != data_1[i]:
            return i
    return i
    

def range_fit(data_0: bytes, data_1: bytes) -> int:
    max_fit = min(len(data_0), len(data_1))
    for i in range(max_fit):
        if data_0[i] != data_1[i]:
            return i
    return max_fit
    

def range_fit(data_0: bytes, data_1: bytes) -> int:
    max_fit = min(len(data_0), len(data_1))
    for i in range(max_fit):
        if data_0[i] != data_1[i]:
            return i
    return max_fit
    
def old_range_diff(
    data_0: bytes, data_1: bytes, max_diff_length: int, min_length_for_fit
) -> Tuple[int, int]:
    index_0_for_0, index_1_for_0 = 0, 0
    index_0_for_1, index_1_for_1 = 0, 0

    check_index_in_range: Callable[
        [int, bytes], bool
    ] = lambda index, data: index < max_diff_length and index < len(data)

    check_if_fit_found: Callable[
        [bytes, bytes, int, int], bool
    ] = lambda index_0, index_1: (
        data_0[index_0:][:min_length_for_fit] == data_1[index_1:][:min_length_for_fit]
    )

    while index_0_for_0 < len(data_0) and index_1_for_1 < len(data_1):
        while True:
            if not check_index_in_range(
                index_1_for_0, data_1
            ) and not check_index_in_range(index_0_for_1, data_0):
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
    return len(data_0), len(data_1)


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
        range_fit(data_0=data_0[index_0:], data_1=data_1[index_1:]) >= min_length_for_fit
    )
    
    results: List[Tuple] = [(len(data_0), len(data_1))]
    results_score: List[int] = [0]
    while index_0_for_0 < len_data_0 and index_1_for_1 < len_data_1:
        while True:
            if not (
                index_1_for_0 < max_diff_length and index_1_for_0 < len_data_1
            ) and not (index_0_for_1 < max_diff_length and index_0_for_1 < len_data_0):
                break

            data_0_fit_len = range_fit(data_0=data_0[index_0_for_0:], data_1=data_1[index_1_for_0:])
            if data_0_fit_len >= min_length_for_fit:
                results.append((index_0_for_0, index_1_for_0))
                results_score.append(data_0_fit_len)
            
            data_1_fit_len = range_fit(data_0=data_0[index_0_for_1:], data_1=data_1[index_1_for_1:])
            if data_1_fit_len >= min_length_for_fit:
                results.append((index_0_for_1, index_1_for_1))
                results_score.append(data_1_fit_len)

            index_1_for_0 += 1
            index_0_for_1 += 1

        index_0_for_0 += 1
        index_1_for_0 = 0
        index_0_for_1 = 0
        index_1_for_1 += 1
    
    return results, results_score
