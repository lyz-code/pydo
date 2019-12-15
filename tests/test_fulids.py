from pydo.manager import pydo_default_config
from pydo.fulids import FulidGenerator

import ulid
import pytest


class TestFulidGenerator:
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
        self.fulid_gen = FulidGenerator(
            pydo_default_config['fulid_characters']['default'],
            pydo_default_config['fulid_forbidden_characters']['default'],
        )

        yield 'setup'

    def test_fulid_gen_has_charset_attribute(self):
        assert self.fulid_gen.charset == \
            list(pydo_default_config['fulid_characters']['default'])

    def test_fulid_gen_has_forbidden_charset_attribute(self):
        assert self.fulid_gen.forbidden_charset == \
            list(pydo_default_config['fulid_forbidden_characters']['default'])

    def test_fulid_generates_an_ulid_object(self):
        id = self.fulid_gen.new()
        assert isinstance(id, ulid.ulid.ULID)

    def test_fulid_generates_an_ulid_with_the_specified_charset(self):
        id = self.fulid_gen.new()

        for character in id.randomness().str:
            assert character.lower() in \
                pydo_default_config['fulid_characters']['default']

    def test_fulid_does_not_accept_invalid_terminal_characters(self):
        with pytest.raises(ValueError):
            FulidGenerator(
                'ilou|&:;()<>~*@?!$#[]{}\\/\'"`',
                pydo_default_config['fulid_forbidden_characters']['default'],
            )
