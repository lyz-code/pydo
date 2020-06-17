from pydo import config
from pydo.fulids import fulid

import datetime
import pytest


class Testfulid:
    """
    Test class to ensure that the fulid object generates the ulids as we
    expect.

    Public attributes:
        alembic (mock): alembic mock.
        homedir (string): User home directory path
        log (mock): logging mock
        session (Session object): Database session.
    """

    @pytest.fixture(autouse=True)
    def setup(self, session):
        self.session = session
        self.fulid = fulid()

        yield 'setup'

    def test_representation(self):
        self.fulid.new()
        assert str(self.fulid.__repr__) == "<bound method fulid.__repr__ of" \
            + " <fulid('{}')>>".format(self.fulid.str)

    def test_fulid_has_charset_attribute(self):
        assert self.fulid.charset == list(config.get('fulid.characters'))

    def test_fulid_has_forbidden_charset_attribute(self):
        assert self.fulid.forbidden_charset == \
            list(config.get('fulid.forbidden_characters'))

    def test_fulid_has_fulid_attribute_none_by_default(self):
        assert self.fulid.str is None

    def test_fulid_has_charset_attribute_set_by_default(self):
        assert self.fulid.charset == list(config.get('fulid.characters'))

    def test_fulid_has_forbidden_charset_attribute_set_by_default(self):
        assert self.fulid.forbidden_charset == \
            list(config.get('fulid.forbidden_characters'))

    def test_fulid_can_set_fulid_attribute(self):
        self.fulid = fulid(fulid='full_fulid_string')
        assert self.fulid.str == 'full_fulid_string'

    def test_fulid_can_set_charset_attribute(self):
        self.fulid = fulid(character_set='ab')
        assert self.fulid.charset == ['a', 'b']

    def test_fulid_can_set_forbidden_charset_attribute(self):
        self.fulid = fulid(forbidden_charset='/')
        assert self.fulid.forbidden_charset == ['/']

    def test_fulid_returns_timestamp(self):
        self.fulid.new()
        assert isinstance(self.fulid.timestamp(), datetime.datetime)

    def test_fulid_returns_randomness(self):
        self.fulid.new()
        assert self.fulid.randomness() == self.fulid.str[10:19]

    def test_fulid_returns_id(self):
        self.fulid.new()
        assert self.fulid.id() == self.fulid.str[19:]

    def test_fulid_new_generates_an_fulid_object(self):
        id = self.fulid.new()
        assert isinstance(id, fulid)

    def test_fulid_generates_an_ulid_with_the_id_in_charset(self):
        for character in self.fulid.new().id():
            assert character.lower() in config.get('fulid.characters')

    def test_fulid_does_not_accept_invalid_terminal_characters(self):
        with pytest.raises(ValueError):
            fulid(
                'ilou|&:;()<>~*@?!$#[]{}\\/\'"`',
                config.get('fulid.forbidden_characters'),
            )

    def test_fulid_sets_the_fulid_attribute(self):
        fulid = self.fulid.new()
        assert len(fulid.str) == 26
        assert isinstance(fulid.str, str)

    def test_fulid_new_returns_first_fulid_if_last_fulid_is_none(self):
        assert self.fulid.new().id() == 'AAAAAAA'

    def test_fulid_from_str_generates_fulid(self):
        assert isinstance(
            self.fulid.from_str('01DW02J8WWJNB109DA0AAAAAAA'),
            fulid
        )

    def test_string_to_number_can_decode_number(self):
        assert self.fulid._decode_id('AAAAAAA') == 0
        assert self.fulid._decode_id('RRRRRRR') == 9999999

    def test_string_to_number_can_decode_fulid_id(self):
        assert self.fulid._decode_id('01DW02J8WWJNB109DA0AAAAAAA') == 0

    def test_string_to_number_raises_error_if_char_not_in_charset(self):
        with pytest.raises(ValueError):
            # 7 is not in the charset
            self.fulid._decode_id('7')

    def test_encode_number_returns_expected_string(self):
        assert self.fulid._encode_id(0) == 'A'
        assert self.fulid._encode_id(999999) == 'RRRRRR'

    def test_encode_number_supports_padding(self):
        assert self.fulid._encode_id(0, 7) == 'AAAAAAA'
        assert self.fulid._encode_id(2, 7) == 'AAAAAAD'

    def test_encode_number_supports_base_different_than_10(self):
        self.fulid.charset = ['a', 's']
        assert self.fulid._encode_id(0) == 'A'
        assert self.fulid._encode_id(2) == 'SA'

    def test_fulid_new_returns_sequential_id(self):
        assert self.fulid.new('01DW02J8WWJNB109DA0AAAAAAA').id() == 'AAAAAAS'

    def test_short_fulids_returns_one_character_if_no_coincidence(self):
        fulids = [
            '01DWF3DM7EH40BTYB4SAAAAAAA',
            '01DWF3ETGBK679178BNAAAAAAS',
            '01DWF3EZYE0ANTCMCSSAAAAAAD',
        ]
        expected_sulids = {
            '01DWF3DM7EH40BTYB4SAAAAAAA': 'a',
            '01DWF3ETGBK679178BNAAAAAAS': 's',
            '01DWF3EZYE0ANTCMCSSAAAAAAD': 'd',
        }
        assert self.fulid.sulids(fulids) == expected_sulids

    def test_short_fulids_returns_two_characters_if_coincidence_in_first(self):
        fulids = [
            '01DWF3DM7EH40BTYB4SAAAAAAA',
            '01DWF3ETGBK679178BNAAAAASA',
            '01DWF3EZYE0ANTCMCSSAAAAAAD',
        ]
        expected_sulids = {
            '01DWF3DM7EH40BTYB4SAAAAAAA': 'aa',
            '01DWF3ETGBK679178BNAAAAASA': 'sa',
            '01DWF3EZYE0ANTCMCSSAAAAAAD': 'ad',
        }
        assert self.fulid.sulids(fulids) == expected_sulids

    def test_expand_sulid_returns_fulid_if_no_coincidence(self):
        fulids = [
            '01DWF3DM7EH40BTYB4SAAAAAAA',
            '01DWF3ETGBK679178BNAAAAAAS',
            '01DWF3EZYE0ANTCMCSSAAAAAAD',
        ]
        assert self.fulid.sulid_to_fulid('a', fulids) == \
            '01DWF3DM7EH40BTYB4SAAAAAAA'

    def test_expand_sulid_errors_if_there_is_more_than_one_coincidence(self):
        fulids = [
            '01DWF3DM7EH40BTYB4SAAAAAAA',
            '01DWF3ETGBK679178BNAAAAASA',
            '01DWF3EZYE0ANTCMCSSAAAAAAD',
        ]
        with pytest.raises(KeyError):
            self.fulid.sulid_to_fulid('a', fulids)

    def test_contract_fulid_returns_sulid(self):
        fulids = [
            '01DWF3DM7EH40BTYB4SAAAAAAA',
            '01DWF3ETGBK679178BNAAAAAAS',
            '01DWF3EZYE0ANTCMCSSAAAAAAD',
        ]
        assert self.fulid.fulid_to_sulid(fulids[0], fulids) == 'a'

    def test_contract_ulid_errors_if_not_found(self):
        fulids = [
            '01DWF3DM7EH40BTYB4SAAAAAAA',
            '01DWF3ETGBK679178BNAAAAASA',
            '01DWF3EZYE0ANTCMCSSAAAAAAD',
        ]
        with pytest.raises(KeyError):
            self.fulid.fulid_to_sulid('non_existent', fulids)
