import pytest
from middleware.job_information_manager import job_information_manager as JIM
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request


class TestJIM(object):
    def test_constructor(self):

        assert 1 == 1
