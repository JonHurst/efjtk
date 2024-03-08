.. _webapp:

Web Application Interface
=========================

The toolkit is hooked up to a web application at https://hursts.org.uk/efj.

The control bar on the left has three sections, "Actions", "Download" and
"Modify":

Actions
-------

The "Actions" section allows data to be moved in and out of the application. To
load an eFJ for processing, either use the "Load" button or use drag and
drop. The eFJ will then appear in the text area on the right. The "Save" and
"Copy" buttons can be used to download the text or copy it to the system
clipboard.

There may also be an "Edit config" button in the "Actions" section. This allows
modification of a mapping between aircraft type and aircraft classification as
described in the download logbook section below.

Download
--------

The "Download" section contains tools that convert the eFJ into other useful
formats:

FCL.050 Logbook
^^^^^^^^^^^^^^^

The Acceptable Means of Compliance (AMC) concerning recording of flight time can
be found `on EASA's website
<https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_.
The "FCL.050 Logbook" button converts the eFJ in the text area on the right into
a standalone HTML file with the suggested layout, minus the simulator columns.
This file can be viewed in any web browser and, since it has no external
dependencies, can be moved around at will. It is also simple enough that it can
be successfully imported into spreadsheets, word processors et cetera. If you
would like a PDF it can be created with your browser's print function, but I
would recommend `Prince XML <https://www.princexml.com>`_ for this purpose; it
produces very high quality output and is free for personal use.

The AMC for FCL.050 requires that each sector is classified as single pilot,
single engine; single pilot, multi engine; or multi crew. The eFJ scheme allows
this information to be recorded on a sector by sector basis but does not specify
a default value to use when no classification flag is added. The expectation is
that these flags will nearly always be omitted, requiring that the
classification is inferred from the aircraft type by the external tool that is
processing the eFJ.

The web interface deals with this by using the local browser storage to maintain
a mapping between type and classification. When you attempt to create an HTML
logbook file, a check is made for any types that are in the eFJ but not in this
mapping and a dialog is presented to gather this information if required. Any
unknown types are initially classified as single pilot, single engine in this
dialog — just click the button next to each type until it is correct, then click
"Save". Note that this storage is managed by the browser, so it will not be
shared across devices and it may be evicted at any time depending on the
policies put in place by the browser supplier; you just need to repeat the
process of setting up the mappings if this happens.

Summary
^^^^^^^

The "Summary" button provides various statistics for the eFJ in the text area on
the right. The results are provided as a standalone HTML file, which can be
viewed in any web browser. Since this has no external dependencies it may be
moved at will. It is also simple enough that it can be imported by spreadsheets,
word processors, et cetera.

The results are in the form of three tables: Roles; Conditions; and Landings:

* The Roles table gives a breakdown of flying hours by role (i.e. p1, p1s, p2,
  put) and aircraft type.
* The Conditions table gives a breakdown of flying hours by flight conditions
  (i.e. VFR vs IFR and day vs night) and aircraft type.
* The Landings table gives a breakdown of the number of day and night landings by
  aircraft type.

Modify
------

The tools in the "Modify eFJ" group modify the eFJ in the text area on the right
in place.

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

is replaced with::

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

is replaced with::

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

is replaced with::

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

is replaced with::

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

is replaced with::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 ins
  BFS/BRS 1800/1900 ins
