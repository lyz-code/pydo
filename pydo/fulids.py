"""
Module to define the friendly ulids.

Classes:
    fulid: Class to generate friendly ulids based on a character set.
"""

import ulid


class fulid:
    """
    Class to generate and manage friendly ulids based on a character set.

    Arguments:
        character_set (str): Characters to generate the id of the fulid.
        forbidden_charset (str): Characters forbidden to generate the id of
            the fulid.
        fulid (str): Optional fulid string to initialize the object.

    Public methods:
        new: Method to create a new friendly ulid.
        timestamp: Method to return the timestamp of a fulid.
        randomness: Method to return the randomness string of a fulid.
        from_str: Method to generate a fulid from a fulid string.
        id: Method to return the id string of a fulid.
        sulid_to_fulid: Expand a sulid into the original fulid.
        sulids: Return the suilds of a list of fulids.
        fulid_to_sulid: Contract a fulid into the corresponding sulid

    Private methods:
        _decode_id: Method to transform an id string into a number.
        _encode_id: Method to transform a number into an id string.

    Public attributes:
        charset (list): List of available characters to build the id.
        forbidden_charset (list): List of forbidden characters to build the id.
        str (str): String representation of the fulid
    """

    def __init__(
        self,
        character_set='asdfghjwer',
        forbidden_charset='ilou|&:;()<>~*@?!$#[]{}\\/\'"`',
        fulid=None,
    ):
        self.charset = list(character_set)
        self.forbidden_charset = list(forbidden_charset)
        self.str = fulid

        forbidden_characters = set(self.charset).intersection(
            self.forbidden_charset
        )
        if len(forbidden_characters) > 0:
            raise ValueError(
                'The characters {} were found in the fulid charset, '
                'but they are forbidden'.format(
                    ', '.join(forbidden_characters)
                )
            )

    def __repr__(self):
        return '<{}({!r})>'.format(self.__class__.__name__, self.str)

    def new(self, last_fulid=None):
        """
        Method to create a new friendly ulid

        Arguments:
            last_ulid (ulid): The last ulid created

        Returns:
            fulid (ulid object): Friendly ulid object
        """

        temp_ulid = ulid.new()

        if last_fulid is None:
            id = 7 * self.charset[0].upper()
        else:
            last_fulid = fulid(
                self.charset,
                self.forbidden_charset,
                last_fulid
            )
            id = self._encode_id(
                self._decode_id(last_fulid.id()) + 1,
                pad=7,
            )

        self.str = ''.join([
            temp_ulid.timestamp().str,
            temp_ulid.randomness().str[:9],
            id,
        ])

        return fulid(
            self.charset,
            self.forbidden_charset,
            self.str
        )

    def from_str(self, fulid_string):
        """
        Method to generate a fulid from a fulid string.

        Arguments:
            fulid_string: String representation of the fulid.


        Returns:
            fulid (fulid object): Fulid object
        """
        return fulid(
            self.charset,
            self.forbidden_charset,
            fulid_string,
        )

    def timestamp(self):
        """
        Method to return the timestamp of a fulid.

        Returns:
            timestamp (datetime object): Timestamp of the fulid.
        """
        return ulid.from_str(self.str).timestamp().datetime

    def randomness(self):
        """
        Method to return the randomness string of a fulid.

        Returns:
            randomness (str): Randomness of the fulid.
        """
        return self.str[10:19]

    def id(self):
        """
        Method to return the id string of a fulid.

        Returns:
            id (str): Id of the fulid.
        """
        return self.str[19:]

    def _decode_id(self, number_string):
        """
        Method to transform a selection string into a number

        Arguments:
            number_string (str): string representing a number with the
                character set or a fulid id string.

        Returns:
            number (int): Decoded number
        """

        if len(number_string) > 7:
            number_string = number_string[-7:]

        num = []
        for character in number_string:
            try:
                num.append(str(self.charset.index(character.lower())))
            except ValueError:
                raise ValueError(
                    'Error decoding {} into a number as character {} is not '
                    'in the configuration fulid.characters'.format(
                        number_string,
                        character,
                    )
                )
        return int(''.join(num))

    def _encode_id(self, number, pad=None):
        """
        Method to transform a selection string into a number

        Arguments:
            number (int): Number to encode.
            pad (int): Pad the number with the necessary digits.

        Returns:
            number_string (str): Encoded number
        """

        base = len(self.charset)
        number_characters = []

        if number == 0:
            number_characters.append(self.charset[0].upper())

        while number != 0:
            remainder = number % base
            if remainder < base:
                number_characters.append(self.charset[remainder].upper())
            number = number // base

        number_string = ''.join(number_characters[::-1])

        if pad is not None and len(number_string) != pad:
            pad_string = self.charset[0].upper() * (pad - len(number_string))
            number_string = pad_string + number_string

        return number_string.upper()

    def sulids(self, fulids):
        """
        Method to shorten the length of the fulids so we need to type less
        while retaining the uniqueness.

        The fulids have several parts the first bytes are an encoding of the
        date, then there is a random part and then is an id.

        Therefore, for all the fulids that come, we're going to transform the
        id to lower and reverse them to search the minimum characters that
        uniquely identify each fulids.

        Once we've got all return the equivalence in a dictionary.

        Arguments:
            fuilds (list): List of fulids to shorten.

        Return
            sulids (dict): List of associations between fulids and sulids.
        """
        work_fulids = [fulid.lower()[::-1] for fulid in fulids]

        char_num = 1
        while True:
            work_sulids = [fulid[:char_num] for fulid in work_fulids]
            if len(work_sulids) == len(set(work_sulids)):
                sulids = {
                    fulids[index]: work_sulids[index][::-1]
                    for index in range(0, len(fulids))
                }
                return sulids
            char_num += 1

    def sulid_to_fulid(self, sulid, fulids):
        """
        Method to expand a sulid into the original fulid

        Arguments:
            sulid (str): sulid to expand
            fulids (list): List of fulids to expand

        Returns:
            fulid (str): fulid that match the sulid.
        """

        # Invert the sulids dictionary so it's searchable
        sulids = {
            value: key
            for key, value in self.sulids(fulids).items()
        }
        try:
            return sulids[sulid]
        except KeyError:
            raise KeyError("No fulid was found with that sulid")

    def fulid_to_sulid(self, fulid, fulids):
        """
        Method to contract a fulid into the equivalent sulid

        Arguments:
            fulid (str): fulid to contract
            fulids (list): List of fulids to expand

        Returns:
            sulid (str): sulid that match the fulid.
        """

        try:
            return self.sulids(fulids)[fulid]
        except KeyError:
            raise KeyError("No fulid was found in that list of fulids")
