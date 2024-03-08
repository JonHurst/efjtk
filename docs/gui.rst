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

This menu activates tools that convert the eFJ into other useful formats:

.. _logbook:

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

The GUI interface deals with this by using an INI format file stored as
``.efjtkrc`` in your home/user directory. When you activate this tool, a check
is made for any types that are in the eFJ but not in the INI file and an editor
is presented to gather any required information. Any unknown types are initially
classified as ``spse`` (single pilot, single engine) — just change ``spse`` to
``spme`` (single pilot, multi engine) or ``mc`` (multi crew) as appropriate then
click "Save". You can edit this file at any time by selecting "File|Edit
Config". If it gets corrupted, just delete ``.efjtkrc`` from your home/user
directory and it will be recreated next time the tool is activated.

Summary
^^^^^^^

The "Summary" tool provides various statistics for the eFJ as a standalone HTML
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


Help
----

The "Help|Online Help" menu item opens this document in your default browser.
The "Help|eFJ Format" opens the documentation of the eFJ parser library at the
section where the eFJ scheme is described in full.
