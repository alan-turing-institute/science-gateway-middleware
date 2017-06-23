import pytest
import middleware as mw


class TestClass(object):
    def test_build_command(self):
        input_data = {'length': 5, 'width': 16}
        output = mw.build_command(input_data)

        assert output is 'echo "$((5 * 16))"'
