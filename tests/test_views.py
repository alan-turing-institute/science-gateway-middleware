import pytest
import middleware.views as mw


class TestClass(object):
    def test_build_command(self):
        input_data = {'length': 5, 'width': 16}
        output = mw.build_command(input_data)

        assert output == 'echo "$((5 * 16))"'
