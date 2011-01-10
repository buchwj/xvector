@echo off

rem ## Simple build script to generate API documentation on Windows systems.
rem ## Both Python and the epydoc package must be installed for this to work.

python -m epydoc.cli --config=epydoc.cfg -v
