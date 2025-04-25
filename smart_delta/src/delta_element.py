from typing import Optional, Tuple, List

from smart_delta.src import (
    REPLACEMENT_MARK,
    REPLACEMENT_SPLIT_MARK,
    INDEX_PAYLOAD_SEPERATOR_MARK,
    UNMARK_MARK,
    REGULAR_MARKS,
    DELETION_MARK,
    INSERTION_MARK,
    ENCODING,
)
from smart_delta.src.delta_utils import replace_signs, split_payload


class DeltaElement:
    def __init__(
        self,
        sign: bytes,
        index: int,
        payload: bytes,
        second_payload: Optional[bytes] = None,
        parsing_needed=False,
    ):
        self.sign = sign
        self.index = index
        self.payload = payload
        self.second_payload = second_payload
        self.is_replacement = self.sign == REPLACEMENT_MARK

        if parsing_needed:
            self.payload, self.second_payload = self.parse_payloads()

    def __repr__(self):
        return str(self)

    def __str__(self) -> str:
        return bytes(self).decode(ENCODING)

    def __bytes__(self) -> bytes:
        payload, second_payload = self.fix_payloads()
        if self.is_replacement:
            payload += REPLACEMENT_SPLIT_MARK + second_payload
        return (
            self.sign
            + str(self.index).encode(ENCODING)
            + INDEX_PAYLOAD_SEPERATOR_MARK
            + payload
        )

    def __eq__(self, other) -> bool:
        if (
            type(other) is DeltaElement
            and other.sign == self.sign
            and other.index == self.index
            and other.payload == self.payload
            and other.second_payload == self.second_payload
        ):
            return True
        return False

        
    def __len__(self) -> int:
        return len(bytes(self))

    def fix_payloads(self) -> Tuple[bytes, bytes]:
        fixed_payload, fixed_second_payload = self.payload, self.second_payload
        for possible_sign in [UNMARK_MARK] + REGULAR_MARKS:
            fixed_payload = replace_signs(
                fixed_payload, possible_sign, UNMARK_MARK + possible_sign
            )
            if self.is_replacement:
                fixed_second_payload = fixed_second_payload.replace(
                    possible_sign, UNMARK_MARK + possible_sign
                )
        return fixed_payload, fixed_second_payload

    def parse_payloads(self) -> List[bytes]:
        if self.sign == REPLACEMENT_MARK:
            payloads = list(split_payload(self.payload))
        else:
            payloads = [self.payload, None]
        for i, payload in enumerate(payloads):
            if not payload:
                continue
            for possible_sign in REGULAR_MARKS:
                payload = payload.replace(UNMARK_MARK + possible_sign, possible_sign)
            payloads[i] = payload.replace(UNMARK_MARK + UNMARK_MARK, UNMARK_MARK)
        return payloads

    def apply_on_data(
        self, base_data: bytes, apply_on_reverse=False, offset=0
    ) -> Tuple[bytes, int]:
        data_with_delta = base_data
        sign = self.sign
        index = self.index
        delta_payload = self.payload

        if apply_on_reverse:
            if sign == DELETION_MARK:
                data_with_delta = (
                    base_data[0 : index + offset]
                    + delta_payload
                    + base_data[index + offset :]
                )
                offset += len(delta_payload)
            if sign == INSERTION_MARK:
                data_with_delta = (
                    base_data[0 : index + offset]
                    + base_data[index + len(delta_payload) + offset :]
                )
                offset -= len(delta_payload)
            if sign == REPLACEMENT_MARK:
                data_with_delta = (
                    base_data[0 : index + offset]
                    + delta_payload
                    + base_data[index + len(self.second_payload) + offset :]
                )
                offset += len(delta_payload) - len(self.second_payload)

        else:
            if sign == DELETION_MARK:
                data_with_delta = (
                    base_data[0:index] + base_data[index + len(delta_payload) :]
                )
            if sign == INSERTION_MARK:
                data_with_delta = base_data[0:index] + delta_payload + base_data[index:]
            if sign == REPLACEMENT_MARK:
                data_with_delta = (
                    base_data[0:index]
                    + self.second_payload
                    + base_data[index + len(delta_payload) :]
                )

        return data_with_delta, offset


def parse_str_delta_element(bytes_delta: bytes) -> DeltaElement:
    sign = bytes_delta[0:1]
    index, payload = bytes_delta[1:].split(INDEX_PAYLOAD_SEPERATOR_MARK, 1)
    index = int(index)

    return DeltaElement(sign=sign, index=index, payload=payload, parsing_needed=True)
