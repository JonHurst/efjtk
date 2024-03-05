.. _command_line:

Command Line Interface
========================

The command line interface works as a filter program, i.e. input comes from
STDIN, output goes to STDOUT and error messages are sent to STDERR.

There are two categories of tools: those that output a modified version of the
input and those that output a file in a different format. For example the first
category includes the ability to insert calculated night flying into the eFJ,
whereas the latter includes the ability to output an HTML logbook.

In the examples below, replace ``efj_file`` with the path to your eFJ. It is
assumed that the toolkit has been installed with ``pip`` or ``pipx`` and as such
the entry point ``efj`` has been made available in a location that is included
in your PATH environmental variable.

Modification
------------

Expand
^^^^^^

The eFJ scheme aims to make it as easy as possible to manually enter flight
data where no better alternative is available. To support this, a couple of
short forms are allowed that infer data from previous data. This tool expands
out these short forms, which makes them more human legible::

  $ efj expand < efj_file

The input::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1000/1100
  / 1200/1300

  +
  / 0900/1000
  / 1100/1200

gives the output::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1000/1100
  BFS/BRS 1200/1300

  2024-01-02
  BRS/BFS 0900/1000
  BFS/BRS 1100/1200


Night
^^^^^

Updates the eFJ with calculated night duration and, where necessary, night landing::

  $ efj night < efj_file

The input::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

gives the output::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 n:20 ln
  BFS/BRS 1800/1900 n

If night duration is already recorded for any sector, that sector is not
updated.


VFR
^^^

Adds a flag to every sector to indicate that it was flown under visual flight
rules::

  $ efj vfr < efj_file

The input::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

gives the output::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 v
  BFS/BRS 1800/1900 v


FO
^^

When no role flag is included, it is assumed that the role was p1. This means
that First Officers must mark each sector as ``p1s``, ``p2`` or ``put``.
Captains, on the other hand, just have to mark sectors where they were PM for
the landing with ``m``. This tool allows First Officers to use ``m`` and then
auto-fill the roles as ``p1s`` or ``p2``. ::

  $ efj fo < efj_file

The input::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 m
  BFS/BRS 1800/1900

gives the output::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 p2 m
  BFS/BRS 1800/1900 p1s


Instructor
^^^^^^^^^^

Adds the ``ins`` flag to any sector that does not already have it. ::

  $ efj ins < efj_file

The input::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

gives the output::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 ins
  BFS/BRS 1800/1900 ins


Conversion
----------


FCL.050 Logbook
^^^^^^^^^^^^^^^

The Acceptable Means of Compliance (AMC) concerning recording of flight time can
be found `on EASA's website
<https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_.
This tool converts the eFJ into a standalone HTML file with the suggested
layout, minus the simulator columns. The created file can then be viewed in any
web browser and, since it has no external dependencies, can be moved around at
will. It is also simple enough that it can be successfully imported into
spreadsheets, word processors et cetera. If you would like a PDF it can be
created with your browser's print function, but I would recommend `Prince XML
<https://www.princexml.com>`_ for this purpose; it produces very high quality
output and is free for personal use.

The AMC for FCL.050 requires that each sector is classified as single pilot,
single engine; single pilot, multi engine; or multi crew. The eFJ scheme allows
this information to be recorded on a sector by sector basis but does not specify
a default value to use when no classification flag is added. The expectation is
that these flags will nearly always be omitted, requiring that the
classification is inferred from the aircraft type by the external tool that is
processing the eFJ.

The command line interface uses an INI file to supply the required extra
information. This INI file can either be referenced with a command line switch
(see below) or placed in one of the default locations: these are ``~/.efjtkrc``
or ``~/.config/efjtkrc``. A template for the INI file can be created by running
the eFJ you are intending to turn into a logbook through the command::

  $ efj config < efj_file

This produces a file that looks something like this::

  [aircraft.classes]
  c152 = spse
  c404 = spse
  c406 = spse
  737 = spse
  a320 = spse

The possible classifications are ``spse`` for single pilot, single engine;
``spme`` for single pilot, multi engine or ``mc`` for multi crew. The example
template would therefore need to be modified to::

  [aircraft.classes]
  c152 = spse
  c404 = spme
  c406 = spme
  737 = mc
  a320 = mc

If the INI file is saved to one of the default locations, the HTML logbook can
be produced with::

  $ efj logbook < efj_file

If you want to keep the INI file in a non-default location, use::

  $ efj logbook --config my_ini_path < efj_file

Summary
^^^^^^^

The summary tool provides various statistics for the eFJ as a standalone HTML
file, which can be viewed in any web browser. Since this has no external
dependencies it may be moved at will. It is also simple enough that it can be
imported by spreadsheets, word processors, et cetera.

The results are in the form of three tables: Roles; Conditions; and Landings:

* The Roles table gives a breakdown of flying hours by role (i.e. p1, p1s, p2,
  put) and aircraft type.
* The Conditions table gives a breakdown of flying hours by flight conditions
  (i.e. VFR vs IFR and day vs night) and aircraft type.
* The Landings table gives a breakdown of the number of day and night landings by
  aircraft type.

::

   $ efj summary < efj_file
