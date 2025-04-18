from typing import List, Optional, Union

from smart_delta.src import (
    ENCODING,
    delta_utils,
)
from smart_delta.src.delta_element import DeltaElement
from smart_delta.src.delta_generator.delta_generator_utils import generate_delta


class DeltaGenerator:
    DEFAULT_MAX_DIFF_LENGTH = 1000
    DEFAULT_MIN_LENGTH_FOR_FIT = 3

    def __init__(
        self,
        data_0: Union[str, bytes],
        data_1: Union[str, bytes],
        min_length_for_fit: Optional[int] = None,
        max_diff_length: Optional[int] = None,
    ):
        self.data_0 = data_0
        self.data_1 = data_1

        if type(self.data_0) is str:
            self.data_0 = bytes(self.data_0, encoding=ENCODING)
        if type(self.data_1) is str:
            self.data_1 = bytes(self.data_1, encoding=ENCODING)

        if min_length_for_fit:
            self.min_length_for_fit = min_length_for_fit
        else:
            self.min_length_for_fit = self.DEFAULT_MIN_LENGTH_FOR_FIT
        if max_diff_length:
            self.max_diff_length = max_diff_length
        else:
            self.max_diff_length = self.DEFAULT_MAX_DIFF_LENGTH

        self.delta_elements: List[DeltaElement] = []

    def generate_delta(self) -> List[DeltaElement]:
        self.delta_elements = generate_delta(
            self.data_0, self.data_1, self.max_diff_length, self.min_length_for_fit
        )
        return self.delta_elements.copy()

    def __bytes__(self):
        delta_string = b""
        for delta_step in self.delta_elements:
            delta_string += bytes(delta_step)
        return delta_string

    def __str__(self):
        return bytes(self).decode(ENCODING)


def range_fit(data_0, data_1) -> int:
    min_len = min(len(data_0), len(data_1))
    for index in range(min_len):
        if data_0[index] != data_1[index]:
            return index
    return min_len
