"""Version constraint engine tests."""

from app.parser.version_parser import Version, satisfies


def test_numeric_ordering_not_lexicographic():
    assert Version.parse("2.10") > Version.parse("2.9")
    assert Version.parse("1.20.1") > Version.parse("1.9.4")


def test_satisfies_operators():
    assert satisfies("1.20.1", ">=1.20")
    assert not satisfies("1.19.4", ">=1.20")
    assert satisfies("1.20.1", "[1.20,1.21)")
    assert not satisfies("1.21", "[1.20,1.21)")
    assert satisfies("5.0.0", "[5.0,)")
    assert satisfies("1.2.3", "*")
    assert satisfies("1.2.3", None)


def test_exact_bracket():
    assert satisfies("1.20.1", "[1.20.1]")
    assert not satisfies("1.20.2", "[1.20.1]")
