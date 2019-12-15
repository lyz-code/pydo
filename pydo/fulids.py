"""
Module to define the friendly ulids.

Classes:
    fulid: Class to generate friendly ulids based on a character set.
"""

import random
import ulid


class FulidGenerator:
    """
    Class to generate friendly ulids based on a character set.

    Arguments:
        character_set (str): Characters to generate the random part of
            the ulid.

    Attributes:
        charset (list): List of available characters to build the random part.
    """

    def __init__(self, character_set, forbidden_charset):
        self.charset = list(character_set)
        self.forbidden_charset = list(forbidden_charset)

        if len(set(self.charset).intersection(self.forbidden_charset)) > 0:
            raise ValueError(
                'There are forbidden characters in the character_set '
                'provided to FulidGenerator'
            )

    def new(self):
        id = ulid.new()

        old_randomness = id.randomness().str

        randomness = [
            random.choice(self.charset)
            for index in range(0, len(old_randomness))
        ]

        randomness_str = ''.join(randomness).upper()

        return ulid.from_str(id.timestamp().str + randomness_str)
