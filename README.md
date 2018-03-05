# Classify Lines Of Code
Count and classify lines of code using a configuration driven, context aware regular expression engine.
There's also some reporting available.

This project is a standard python package, install with `pip` or your favourite python package installer.

## Usage

See `cloc -h` after installing.


## How and Why

My theory was that well designed code libraries are not only well tested, i.e. have good coverage, but that they also promote high developer velocity.  That means the unit tests are small (test one thing at a time) but also that changes to the code, to introduce new features for example, require a relatively small number of changes to test and test fixture code.
I wanted to test this theory, but I couldn't find a line of code counter that would allow me to classify lines of code into things like test code, test fixture code, etc. so I wrote this.
The program reads configuration from YAML or JSON files, then for each line in each file in the project match to an entry in the configuration and store the classified line.  At the end of the process the list of classified lines is passed to a reporter for display.
