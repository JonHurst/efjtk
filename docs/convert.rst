Conversion
==========

Config
------

To create an FCL.050 compliant logbook from an eFJ requires knowledge of
whether each type of aircraft is single pilot, single engine; single pilot,
multi engine; or multi crew. The eFJ format allows overrides to be specified on
a sector by sector basis, but leaves it to tooling to determine defaults.

The efjtk logbook tool uses an INI file to supply this knowledge. To help with
creation of this INI file, a tool is provided to create a template: ::

  efj config < my_efj > output

will give output something like this: ::

  [aircraft.classes]
  c152 = spse
  c406 = spse
  737 = spse
  a320 = spse

This should be edited to provide the correct values: ::

  [aircraft.classes]
  c152 = spse
  c406 = spme
  737 = mc
  a320 = mc

For UNIX operating systems, this should be saved to either ``~/.efjtkrc`` or
``~/.config/efjtkrc``. For Windows it should be saved in your home directory as
``.efjtkrc``. It can also be saved elsewhere and specified with the
``--config`` command line option.
