import pytest

from add_numbers import add_numbers

# Unit tests using pytest with decorators
@pytest.mark.parametrize('a, b, expected', [
    (2, 2, 4),
    (-1, 1, 0),
    (-1, -1, -2),
    (0, 0, 0),
    (1.5, 2.5, 4.0)
])
def test_add_numbers(a, b, expected):
    assert add_numbers(a, b) == expected
