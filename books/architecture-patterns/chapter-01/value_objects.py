from collections import namedtuple
from dataclasses import dataclass
from typing import NamedTuple

import pytest


@dataclass(frozen=True)
class Name:
    first_name: str
    surname: str


class Money(NamedTuple):
    currency: str
    value: int


Line = namedtuple('Line', ['sku', 'qty'])


def test_equality():
    assert Money("gbp", 10) == Money("gbp", 10)
    assert Name("Harry", "Percival") != Name("Bob", "Gregory")
    assert Line("RED-CHAIR", 5) == Line("RED-CHAIR", 5)


fiver = Money("gbp", 5)
tenner = Money("gbp", 10)


def test_can_add_money_values_for_the_same_currency():
    assert fiver + fiver == tenner


def test_can_subtract_money_values():
    assert tenner - fiver == fiver


def test_adding_different_currencies_fails():
    with pytest.raises(ValueError):
        Money("usd", 10) + Money("gbp", 25)


def test_can_multiply_monet_by_a_number():
    assert fiver * 5 == Money("gbp", 25)


def test_multiplying_two_money_values_is_an_error():
    with pytest.raises(ValueError):
        tenner * tenner


def test_name_equality():
    assert Name("Harry", "Percival") != Name("Barry", "Percival")


class Person:
    def __init__(self, name: Name):
        self.name = name


def test_barry_is_harry():
    harry = Person(Name("Harry", "Percival"))
    barry = harry

    barry.name = Name("Barry", "Percival")

    assert harry is barry and barry is harry
