.. _gui:

Graphical User Interface
========================

This is a simple, cross platform, Tk based Graphical Interface. A text file with
an electronic Flight Journal scheme is loaded with the "File|Open" menu item.
This will be shown with simple syntax highlighting in the basic text editor that
fills the main area of the window. All menu items will then apply to the text in
this area.

The menu bar provides "File", "Edit", "Modify", "Export" and "Help" sub-menus:

File
----

The "Open", "Save", "Save As" and "Quit" menu items should hopefully be
self-explanatory. The "Edit Config" item is described in :ref:`the "Export|FCL.050
Logbook" section below <logbook>`.

Edit
----

All the menu items under the "Edit" menu should be self-explanatory.


Modify
------

The tools in the "Modify" submenu modify the eFJ in place. If some text is
selected in the text editor (e.g. with a mouse), only lines with selected text
are modified.

Expand
^^^^^^

The eFJ scheme aims to make it as easy as possible to manually enter flight
data where no better alternative is available. To support this, a couple of
short forms are allowed that infer data from previous data. This tool expands
out these short forms, which makes them more human legible.

::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1000/1100
  / 1200/1300

  +
  / 0900/1000
  / 1100/1200

becomes::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1000/1100
  BFS/BRS 1200/1300

  2024-01-02
  BRS/BFS 0900/1000
  BFS/BRS 1100/1200


Night
^^^^^

Updates eFJ with calculated night duration and, where necessary, night landing.

::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

becomes::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 n:20 ln
  BFS/BRS 1800/1900 n

If night duration is already recorded for any sector, that sector is not
updated.


VFR
^^^

Adds a flag to every sector to indicate that it was flown under visual flight rules.

::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

becomes::

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
auto-fill the roles as ``p1s`` or ``p2``.

::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 m
  BFS/BRS 1800/1900

becomes::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 p2 m
  BFS/BRS 1800/1900 p1s


Instructor
^^^^^^^^^^

Adds the ``ins`` flag to any sector that does not already have it.

::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

becomes::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 ins
  BFS/BRS 1800/1900 ins


Export
------

The tools on this menu produce standalone HTML files. These files have no
dependencies, so can be copied and moved around at will. They can be opened in
any reasonably modern web browser, spreadsheet or word processing program.

.. _logbook:

FCL.050 Logbook
^^^^^^^^^^^^^^^

The EASA Acceptable Means of Compliance with regards to the recording of
personal flight records can be found `in section FCL.050 of EASA's website
<https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_.
This format has also been adopted by the UK CAA.

The logbook tool converts the eFJ into a standalone HTML file containing flight
records in the FCL.050 layout. When the tool is activated a dialog is presented
to allow the dates included in the output file to be restricted; these dates are
initially set to include all entries in the input file.

The AMC for FCL.050 requires that each sector is classified as single pilot,
single engine; single pilot, multi engine; or multi crew. The classification
associated with a given type is usually encoded into the eFJ on the first
occasion that a new type is flown using the extended aircraft syntax, e.g.
``G-ABCD:A320:mc`` recorded on the first occasion an A320 is flown results in a
future sector preceded by ``G-EFGH:A320`` also being classified as multi-crew.

To allow for processing of eFJ fragments that do not include an entry with the
extended syntax, a secondary mechanism for linking types to classifications is
available. This uses an INI format file stored as ``.efjtkrc`` in your home/user
directory. When you activate the logbook tool, an attempt is made to look up any
unclassified types in this INI file. If this fails a dialog presents an updated
INI file with the type initially classified as ``spse`` — just change
``spse`` to ``spme`` (single pilot, multi engine) or ``mc`` (multi crew) if
appropriate then click "Save". You can edit this file at any time by selecting
"File|Edit Config". If it gets corrupted, just delete ``.efjtkrc`` from your
home/user directory and it will be recreated next time the tool is activated.

Summary
^^^^^^^

The summary tool provides various statistics for the eFJ as a standalone HTML
file.

The results include a breakdown of flying roles, aircraft classes, conditions
and landings by aircraft type, and all relevant totals.

The instructions for creating and using an INI file to specify aircraft classes,
as described above for the logbook tool, also apply to the summary tool.

Cumulative Totals
^^^^^^^^^^^^^^^^^

The cumulative totals tool provides the cumulative totals for every entry in an
FCL.050 logbook as a standalone HTML file.

When a date range is specified, this only restricts the dates included in the
output; the calculation still includes all entries.

The instructions for creating and using an INI file to specify aircraft classes,
as described above for the logbook tool, also apply to the cumulative totals
tool.


Help
----

The "Help|Online Help" menu item opens this document in your default browser.
The "Help|eFJ Format" opens the documentation of the eFJ parser library at the
section where the eFJ scheme is described in full.
