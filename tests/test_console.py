
"""
Unit tests for IO module.

"""


from elicit import console


class TestIO:

    def test_create(self):
        """Test object instantiation."""
        uio = console.ConsoleIO()
        assert uio

    def test_create_with_prompt(self):
        """Test object instantiation."""
        uio = console.ConsoleIO(pagerprompt="-more-")
        assert uio


if __name__ == '__main__':
    import pytest
    pytest.main(args=["-s", __file__])
