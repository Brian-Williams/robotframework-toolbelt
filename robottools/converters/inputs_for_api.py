import re

cli_options = """
-F, --extension <value>
Parse only these files when executing a directory.
-N, --name <name>
Sets the name of the top-level test suite.
-D, --doc <document>
Sets the documentation of the top-level test suite.
-M, --metadata <name:value>
Sets free metadata for the top level test suite.
-G, --settag <tag>
Sets the tag(s) to all executed test cases.
-t, --test <name>
Selects the test cases by name.
-s, --suite <name>
Selects the test suites by name.
-R, --rerunfailed <file>
Selects failed tests from an earlier output file to be re-executed.
-S, --rerunfailedsuites <file>
Selects failed test suites from an earlier output file to be re-executed.
-i, --include <tag>
Selects the test cases by tag.
-e, --exclude <tag>
Selects the test cases by tag.
-c, --critical <tag>
Tests that have the given tag are considered critical.
-n, --noncritical <tag>
Tests that have the given tag are not critical.
-v, --variable <name:value>
Sets individual variables.
-V, --variablefile <path:args>
Sets variables using variable files.
-d, --outputdir <dir>
Defines where to create output files.
-o, --output <file>
Sets the path to the generated output file.
-l, --log <file>
Sets the path to the generated log file.
-r, --report <file>
Sets the path to the generated report file.
-x, --xunit <file>
Sets the path to the generated xUnit compatible result file.
--xunitskipnoncritical
Mark non-critical tests on xUnit compatible result file as skipped.
-b, --debugfile <file>
A debug file that is written during execution.
-T, --timestampoutputs
Adds a timestamp to all output files.
--splitlog	Split log file into smaller pieces that open in browser transparently.
--logtitle <title>
Sets a title for the generated test log.
--reporttitle <title>
Sets a title for the generated test report.
--reportbackground <colors>
Sets background colors of the generated report.
-L, --loglevel <level>
Sets the threshold level for logging. Optionally the default visible log level can be given separated with a colon (:).
--suitestatlevel <level>
Defines how many levels to show in the Statistics by Suite table in outputs.
--tagstatinclude <tag>
Includes only these tags in the Statistics by Tag table.
--tagstatexclude <tag>
Excludes these tags from the Statistics by Tag table.
--tagstatcombine <tags:title>
Creates combined statistics based on tags.
--tagdoc <pattern:doc>
Adds documentation to the specified tags.
--tagstatlink <pattern:link:title>
Adds external links to the Statistics by Tag table.
--removekeywords <all|passed|name:pattern|tag:pattern|for|wuks>
Removes keyword data from the generated log file.
--flattenkeywords <for|foritem|name:pattern|tag:pattern>
Flattens keywords in the generated log file.
--listener <name:args>
Sets a listener for monitoring test execution.
--warnonskippedfiles
Show a warning when an invalid file is skipped.
--nostatusrc	Sets the return code to zero regardless of failures in test cases. Error codes are returned normally.
--runemptysuite
Executes tests also if the selected test suites are empty.
--dryrun	In the dry run mode tests are run without executing keywords originating from test libraries. Useful for validating test data syntax.
-X, --exitonfailure
Stops test execution if any critical test fails.
--exitonerror	Stops test execution if any error occurs when parsing test data, importing libraries, and so on.
--skipteardownonexit
Skips teardowns is test execution is prematurely stopped.
--prerunmodifier <name:args>
Activate programmatic modification of test data.
--prerebotmodifier <name:args>
Activate programmatic modification of results.
--randomize <all|suites|tests|none>
Randomizes test execution order.
--console <verbose|dotted|quiet|none>
Console output type.
--dotted	Shortcut for --console dotted.
--quiet	Shortcut for --console quiet.
-W, --consolewidth <width>
Sets the width of the console output.
-C, --consolecolors <auto|on|ansi|off>
Specifies are colors used on the console.
-K, --consolemarkers <auto|on|off>
Show markers on the console when top level keywords in a test case end.
-P, --pythonpath <path>
Additional locations to add to the module search path.
-E, --escape <what:with>
Escapes characters that are problematic in the console.
-A, --argumentfile <path>
A text file to read more arguments from.
-h, --help	Prints usage instructions.
--version	Prints the version information.
"""

post_processing = """
-R, --merge	Changes result combining behavior to merging.
-N, --name <name>
 	Sets the name of the top level test suite.
-D, --doc <document>
 	Sets the documentation of the top-level test suite.
-M, --metadata <name:value>
 	Sets free metadata for the top-level test suite.
-G, --settag <tag>
 	Sets the tag(s) to all processed test cases.
-t, --test <name>
 	Selects the test cases by name.
-s, --suite <name>
 	Selects the test suites by name.
-i, --include <tag>
 	Selects the test cases by tag.
-e, --exclude <tag>
 	Selects the test cases by tag.
-c, --critical <tag>
 	Tests that have the given tag are considered critical.
-n, --noncritical <tag>
 	Tests that have the given tag are not critical.
-d, --outputdir <dir>
 	Defines where to create output files.
-o, --output <file>
 	Sets the path to the generated output file.
-l, --log <file>
 	Sets the path to the generated log file.
-r, --report <file>
 	Sets the path to the generated report file.
-x, --xunit <file>
 	Sets the path to the generated xUnit compatible result file.
--xunitskipnoncritical
 	Mark non-critical tests on xUnit compatible result file as skipped.
-T, --timestampoutputs
 	Adds a timestamp to all output files.
--splitlog	Split log file into smaller pieces that open in browser transparently.
--logtitle <title>
 	Sets a title for the generated test log.
--reporttitle <title>
 	Sets a title for the generated test report.
--reportbackground <colors>
 	Sets background colors of the generated report.
-L, --loglevel <level>
 	Sets the threshold level to select log messages. Optionally the default visible log level can be given separated with a colon (:).
--suitestatlevel <level>
 	Defines how many levels to show in the Statistics by Suite table in outputs.
--tagstatinclude <tag>
 	Includes only these tags in the Statistics by Tag table.
--tagstatexclude <tag>
 	Excludes these tags from the Statistics by Tag table.
--tagstatcombine <tags:title>
 	Creates combined statistics based on tags.
--tagdoc <pattern:doc>
 	Adds documentation to the specified tags.
--tagstatlink <pattern:link:title>
 	Adds external links to the Statistics by Tag table.
--removekeywords <all|passed|name:pattern|tag:pattern|for|wuks>
 	Removes keyword data from the generated outputs.
--flattenkeywords <for|foritem|name:pattern|tag:pattern>
 	Flattens keywords in the generated outputs.
--starttime <timestamp>
 	Sets the starting time of test execution when creating reports.
--endtime <timestamp>
 	Sets the ending time of test execution when creating reports.
--nostatusrc	Sets the return code to zero regardless of failures in test cases. Error codes are returned normally.
--processemptysuite
 	Processes output files even if files contain empty test suites.
--prerebotmodifier <name:args>
 	Activate programmatic modification of results.
-C, --consolecolors <auto|on|ansi|off>
 	Specifies are colors used on the console.
-P, --pythonpath <path>
 	Additional locations to add to the module search path.
-E, --escape <what:with>
 	Escapes characters that are problematic in the console.
-A, --argumentfile <path>
 	A text file to read more arguments from.
-h, --help	Prints usage instructions.
--version	Prints the version information.
"""

options = cli_options + post_processing


def get_option(line):
    try:
        return re.search("(?<=--)\w+", line).group(0)
    except AttributeError:
        pass


def get_inputs(line):
    try:
        return re.search("(?<=<).+(?=>)", line).group(0)
    except AttributeError:
        pass


def get_inline_doc(line, option):
    if line.endswith("."):
        try:
            return re.split(">|{}".format(option), line, 1)[1]
        except IndexError:
            raise RuntimeError(line)


def get_properties_for_api(options_sting):
    templated_options = []
    option = inputs = doc = None
    for line in options.splitlines():
        if not option:
            option = get_option(line)
            inputs = get_inputs(line)
            doc = get_inline_doc(line, option)
        else:
            doc = line

        if option and doc and option not in templated_options:
            templated_options.append(option)

            type = "string" if inputs else "boolean"
            prop = """
{}:
  type: {}
  description: {}""".format(option, type, doc)
            if inputs:
                if "|" in inputs and ":" not in inputs:
                    enums = "[" + ', '.join(inputs.split('|')) + "]"
                    addon = "enum: {}".format(enums)
                else:
                    addon = "example: {}".format(inputs)
                prop += "\n  " + addon
            option = inputs = doc = None
            print(prop.strip())


if __name__ == "__main__":
    get_properties_for_api(options)
