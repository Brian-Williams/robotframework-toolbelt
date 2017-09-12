# Helpful robot tools

## rename
Rename a suite and save the original name as 'originallongname' metadata.

## resetname
Reapply the 'originallongname' metadata and set as the suite name.

## rerunrenamedtests
Runs resetname and then gathers failed tests to be run.

## rerunrenamedsuties
Runs resetname and then gathers failed suites to be run.

## unname
Sets the name of a named (-N or --name) or renamed (prerunmodifier rename:) suite back to
it's original name as if it was set as default without either input.
