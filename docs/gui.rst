.. _gui:

Graphical User Interface
========================

This is a simple, cross platform, Tk based Graphical Interface. A text file with
an electronic Flight Journal scheme is loaded with the "File|Open" menu item.
This will be shown with simple syntax highlighting in the basic text editor that
fills the main area of the window. All menu items will then apply to the text in
this area.

The menu bar provides "File", "Edit", "Modify", "Export" and "Help" sub-menus.
The "File", "Edit" and "Help" sub-menus should hopefully be self-explanatory.
For the "Modify" and "Export" sub-menus:

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
the landing with ``m``. This tool allows First Officers to also just use ``m``
and then auto-fill the roles as ``p1s`` or ``p2`` by assuming their role was p1s
if they landed the aircraft and p2 if they did not.

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

The `EASA FCL.050 Acceptable Means of Compliance
<https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_,
which has also been adopted by the UK CAA, details the format required for
personal flight records. The FCL.050 Logbook tool converts an eFJ into a
compliant, standalone, HTML file.

Summary
^^^^^^^

The Summary tool provides various statistics for the eFJ as a standalone HTML
file.

The results include a breakdown of flying roles, aircraft classes, conditions
and landings by aircraft type, and all relevant totals.


Cumulative Totals
^^^^^^^^^^^^^^^^^

The cumulative totals tool provides the cumulative totals for every sector as a
standalone HTML file.

When a date range is specified, this only restricts the dates included in the
output; the calculation still includes all entries.


Help
----

The "Help|Online Help" menu item opens this document in your default browser.
The "Help|eFJ Format" opens the documentation of the eFJ parser library at the
section where the eFJ scheme is described in full.
