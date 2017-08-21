from robot.api import SuiteVisitor


class rename(SuiteVisitor):
    """Store the original longname so that rerunning can happen even with virtually reorganized tests."""

    def __init__(self, new_name):
        self.new_name = new_name

    def start_suite(self, suite):
        originallongname = suite.longname
        suite.metadata.setdefault('originallongname', originallongname)
        suite.configure(name=self.new_name)
