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

Logbook
-------

This tool generates a standalone HTML file that complies with `EASA AMC1
FCL.050
<https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=2&regulatory-subject=Part-FCL#_Toc256000052>`_.
This file has no external dependencies and can thus be safely moved around and
opened with any browser. It has been kept deliberately simple, so it will also
import well into spreadsheets, word processors etc. If you would like it as
a PDF, `Prince XML <https://www.princexml.com>`_ works very well, and has a
free version for personal use.

As described in the section above, this tool needs additional information about
aircraft categorisation provided by an INI file. If this INI file is in one of
the default locations, the command is simply: ::

  efj logbook < input > output.html

If the INI is in a non-default location, use: ::

  efj logbook --config my.ini < input > output.html

The input: ::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1000/1100
  BFS/BRS 1200/1300 m

  2024-01-02
  BRS/BFS 0900/1000 m
  BFS/BRS 1100/1200

would `generate this output <_static/output.html>`_.


Summary
-------

This tool summarises the eFJ data. It creates a standalone HTML file
incorporating three tables:

1. Hours flown by aircraft type and pilot role.
2. Hours flown by aircraft type and conditions (VFR/IFR, day/night).
3. Landings by aircraft type and day/night.

This file has no external dependencies, so it can safely be moved around and
opened with any web browser. It also imports well into spreadsheets, word
processors etc.

::

   efj summary < input > output.html

The input: ::

  2024-01-01
  { CP:Bloggs }
  G-ABCD:A320
  BRS/BFS 1000/1100 p1s
  BFS/BRS 1200/1300 p2 m

  2024-01-02
  G-EFGH:A321
  BRS/BFS 0900/1000 p2 m
  BFS/BRS 1100/1200 p1s

would `generate this summary <_static/summary.html>`_.
