.. _command_line:

Command Line Interface
========================

The command line interface works as a filter program, i.e. input comes from
STDIN, output goes to STDOUT and error messages are sent to STDERR.

There are two categories of tools: those that output a modified version of the
input and those that output a file in a different format. For example, the first
category includes the ability to insert calculated night flying into the eFJ,
whereas the latter includes the ability to output an HTML logbook.

The ``‑‑from`` and ``‑‑to`` switches specify the range of dates to be
considered. These take an ISO 8601 date, either of the form ``2026‑09‑21`` or
the form ``20260921``. Entries dated on or after the ``‑‑from`` date but before
the ``‑‑to`` date are included. If the ``‑‑from`` switch is omitted, it is set
to the first date in the source text. If the ``‑‑to`` switch is omitted, it is
set to the day after the last date in the source text. For tools that modify the
input, all entries falling outside this range will pass through unchanged. Tools
that output a file in a different format will only include dates within the
range in the output.

The logbook, cumulative totals and summary tools produce standalone HTML files.
These files have no dependencies, so can be copied and moved around at will.
They can be opened in any reasonably modern web browser, spreadsheet or word
processing program. The gross error check tool produces simple text output.

The tools producing HTML files require that each sector is classified as either
single pilot, single engine; single pilot, multi engine; or multi crew. The
classification associated with a given type is usually encoded into the eFJ on
the first occasion that a new type is flown using the extended aircraft syntax,
e.g. ``G-ABCD:C406:spme`` recorded on the first occasion a Cessna 406 is flown
results in a future sector preceded by ``G-EFGH:C406`` also being classified as
single pilot, multi-engine. Where a type has not been classified, it is
defaulted to multi-crew.

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
the landing with ``m``. This tool allows First Officers to also just use ``m``
and then auto-fill the roles as ``p1s`` or ``p2`` by assuming their role was p1s
if they landed the aircraft and p2 if they did not. ::

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


FCL.050 Compliant Logbook
^^^^^^^^^^^^^^^^^^^^^^^^^

The `EASA FCL.050 Acceptable Means of
Compliance <https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_,
which has also been adopted by the UK CAA, details the format required for
personal flight records. The logbook tool converts an eFJ into a compliant,
standalone, HTML file.

The command for creating the logbook is::

  $ efj logbook < efj_file


Cumulative Totals
^^^^^^^^^^^^^^^^^

The cumulative totals tool provides the cumulative totals for every entry in an
FCL.050 logbook as a standalone HTML file. This can be very useful if a paper
logbook is being kept updated in parallel with the eFJ.

When a date range is specified, this only restricts the dates included in the
output; the calculation still includes all entries.

The command for the cumulative total tool is::

  $ efj cumulative < efj_file


Summary
^^^^^^^

The summary tool provides various statistics for the eFJ as a standalone HTML
file.

The results include a breakdown of flying roles, aircraft classes, conditions
and landings by aircraft type, and all relevant totals.

The command for the summary tool is::

  $ efj summary < efj_file


Gross Error Check
^^^^^^^^^^^^^^^^^

The gross error check tool flags up suspicious turn-around times, suspicious
airfields or suspicious average velocities.

The “Overlapping” section highlights any sector with a turn-around time of less
than 15 minutes. The date and time of the sector, along with the calculated
turn-around time from the previous sector are provided.

The “Unknown Airfields” section lists airfields with ICAO or IATA codes that are
not in the toolkit's database. This is often due to an airfield closing leading
to its IATA (three letter) code being discontinued; the ICAO (four letter) code
for these airfields usually remain valid.

The “Anomalous Velocity” section highlights any sector over 100nm where the
average velocity, found by dividing the great circle distance between the
airfields by sector time, is not between 50kt and 500kt. The date, times,
destinations, great circle distances and average velocities for these sectors
are tabulated.

The command for the gross error check tool is::

  $ efj gec < efj_file
