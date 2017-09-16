from .docstring import DocTestParser
from testlink import TestLinkHelper, TestlinkAPIGeneric
from robot.libraries.BuiltIn import BuiltIn
from robot.api import logger as robot_logger


reportTCResultParams = [
    'testcaseid', 'testplanid', 'buildname', 'status', 'notes', 'testcaseexternalid', 'buildid', 'platformid',
    'platformname', 'guess', 'bugid', 'custumfields', 'overwrite', 'user', 'execduration', 'timestamp', 'steps',
    'devKey']
report_params = {str(param): 'testlink' + str(param) for param in reportTCResultParams}


class reporttestlink(object):
    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, test_prefix, dev_key, server, *report_kwargs):
        """
        This is specifically for looking at testcaseexternalids in testcase documentation and sending results to all
        testcases found.

        If you would like to set a default input from the test itself you can add 'testlink' to the beginning of the
        parameter and it will select and add if it wasn't passed in at __init__.
        For example if you wanted to pass in the platformname you would set testlinkplatformname. This is to avoid
        robot name collisions with incredibly common variable names like user and timestamp.
        Note: dev_key is set during testlink connection and used as a default by the testlink library.
              So, if `testlinkdevkey` is passed in it will effectively take priority as the second positional arg
              dev_key is *not* put into report_kwargs. This is by design.

        Since kwargs are not supported in listeners you must pass in args with an equal sign between the key and the
        value (<argument>=<value).

        :param test_prefix: The letters preceding testlink numbers. ex. abc-1234 the test_prefix would be 'abc'
        :param dev_key: API key of the user running the tests
        :param server: The testlink server
        :param report_kwargs: These are args in the format `<argument>=<value>`.
        """
        self.test_prefix = test_prefix
        self.dev_key = dev_key
        self.testlink_server = server

        # Listeners don't support real kwargs
        self.report_kwargs = {}
        for kwarg in report_kwargs:
            try:
                arg, value = kwarg.split('=')
            except ValueError:
                raise RuntimeError("Report kwarg was passed in without equal sign. '{}'".format(kwarg))
            if isinstance(value, list):
                raise RuntimeError("Report kwarg was passed in with multiple equal signs. '{}'".format(kwarg))
            self.report_kwargs[arg] = value

        self._tlh = self._platformname = None

    @property
    def tlh(self):
        if not self._tlh:
            self.connect_testlink()
        return self._tlh

    def connect_testlink(self):
        self._tlh = TestLinkHelper(self.testlink_server, self.dev_key).connect(TestlinkAPIGeneric)

    def _get_params_from_variables(self):
        for testlink_param, robot_variable in report_params.items():
            # setdefault but only if real non-None value from test
            if testlink_param not in self.report_kwargs:
                tc_report_val = BuiltIn().get_variable_value("${" + str(robot_variable) + "}")
                if tc_report_val is not None:
                    self.report_kwargs[testlink_param] = tc_report_val

    def _get_testlink_status(self, test):
        # testlink accepts p/f for passed and failed
        status = 'f'
        if test.passed:
            status = 'p'
        return status

    def _get_testcases(self, test):
        return DocTestParser(self.test_prefix).get_testcases(test)

    def end_test(self, data, test):
        testcases = self._get_testcases(test)
        self.report_kwargs['status'] = self._get_testlink_status(test)
        self._get_params_from_variables()

        # This is supposed to default to true by the API spec, but doesn't on some testlink versions
        self.report_kwargs.setdefault('guess', True)

        for testcase in testcases:
            resp = self.tlh.reportTCResult(testcaseexternalid=testcase, **self.report_kwargs)
            robot_logger.info(resp, also_console=True)
