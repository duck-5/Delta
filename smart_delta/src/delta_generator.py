import time
from typing import List, Optional, Union

from smart_delta.src import (
    INSERTION_MARK,
    DELETION_MARK,
    REPLACEMENT_MARK,
    ENCODING,
    delta_utils,
)
from smart_delta.src.delta_element import DeltaElement
import logging
import tqdm


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

        self.logger = logging.getLogger("Delta")
        logging.basicConfig(level=logging.INFO)

    def generate_delta(self) -> List[DeltaElement]:
        starting_time = time.time()
        with tqdm.tqdm(
            total=max(len(self.data_0), len(self.data_1)), unit="b", colour="green"
        ) as pbar:
            result = self._generate_delta(pbar)
        
        delta_size_kb = sum([len(ele) for ele in result])/1000
        self.logger.info(
            f"Finished operation in {time.time() - starting_time:.3f} seconds\n"
            f"Detected {len(result)} changes that sum up to {delta_size_kb} kb\n"
            f"Delta ratio (delta file size / original file size) =  {delta_size_kb / (len(self.data_0)/1000):.3f}"
        )
        return result

    def _generate_delta(self, pbar) -> List[DeltaElement]:
        diff_beginning_index_0 = None
        self.delta_elements = []

        index_0, index_1 = 0, 0
        while index_0 < len(self.data_0) and index_1 < len(self.data_1):
            if self.data_0[index_0] != self.data_1[index_1]:
                diff_beginning_index_0 = index_0
                diff_beginning_index_1 = index_1
                diff_ending_0, diff_ending_1 = delta_utils.range_diff(
                    data_0=self.data_0[diff_beginning_index_0:],
                    data_1=self.data_1[diff_beginning_index_1:],
                    max_diff_length=self.max_diff_length,
                    min_length_for_fit=self.min_length_for_fit,
                )
                pbar.update(max(diff_ending_0, diff_ending_1))

                diff_ending_0 += diff_beginning_index_0
                diff_ending_1 += diff_beginning_index_1

                delta_element = self.create_delta_element(
                    diff_beginning_index_0,
                    diff_ending_0,
                    diff_beginning_index_1,
                    diff_ending_1,
                )
                if delta_element is not None:
                    self.delta_elements.append(delta_element)

                index_0 = diff_ending_0 - 1
                index_1 = diff_ending_1 - 1

                diff_beginning_index_0 = None

            index_0 += 1
            index_1 += 1
            pbar.update(1)

        if not diff_beginning_index_0:
            diff_beginning_index_0 = index_0
            diff_beginning_index_1 = index_1
        if index_0 < len(self.data_0) and index_1 >= len(self.data_1):
            self.delta_elements.append(
                DeltaElement(
                    DELETION_MARK,
                    diff_beginning_index_1,
                    self.data_0[diff_beginning_index_0:],
                )
            )

        if index_1 < len(self.data_1) and index_0 >= len(self.data_0):
            self.delta_elements.append(
                DeltaElement(
                    INSERTION_MARK,
                    diff_beginning_index_1,
                    self.data_1[diff_beginning_index_1:],
                )
            )
        pbar.update(len(self.delta_elements[-1]))
        return self.delta_elements

    def create_delta_element(
        self,
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
                self.data_0[diff_beginning_index_0:diff_ending_0],
            )

        if (
            diff_ending_1 != diff_beginning_index_1
            and diff_ending_0 == diff_beginning_index_0
        ):
            return DeltaElement(
                INSERTION_MARK,
                diff_beginning_index_1,
                self.data_1[diff_beginning_index_1:diff_ending_1],
            )

        if (
            diff_ending_0 != diff_beginning_index_0
            and diff_ending_1 != diff_beginning_index_1
        ):
            return DeltaElement(
                REPLACEMENT_MARK,
                diff_beginning_index_1,
                self.data_0[diff_beginning_index_0:diff_ending_0],
                self.data_1[diff_beginning_index_1:diff_ending_1],
            )

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
