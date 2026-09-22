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

Download
--------

The "Download" section contains tools that convert the eFJ to various standalone
HTML files, which are then downloaded by your browser. These files have no
dependencies, so can be copied and moved around at will. They can be opened in
any reasonably modern web browser, spreadsheet or word processing program.

FCL.050 Logbook
^^^^^^^^^^^^^^^

The `EASA FCL.050 Acceptable Means of
Compliance <https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_,
which has also been adopted by the UK CAA, details the format required for
personal flight records. The logbook tool converts an eFJ into a compliant,
standalone, HTML file.

Summary
^^^^^^^

The summary tool provides various statistics for the eFJ as a standalone HTML
file.

The results include a breakdown of flying roles, aircraft classes, conditions
and landings by aircraft type, and all relevant totals.

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
the landing with ``m``. This tool allows First Officers to also just use ``m``
and then auto-fill the roles as ``p1s`` or ``p2`` by assuming their role was p1s
if they landed the aircraft and p2 if they did not.

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
