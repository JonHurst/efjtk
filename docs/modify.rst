Modification
============

Expand
------

The eFJ format aims to make it as easy as possible to manually enter flight
data where no better alternative is available. To support this, a couple of
short forms are allowed that infer data from previous data. This tool expands
out these short forms, which makes them more human legible.

::

   efj expand < input > output

The input: ::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1000/1100
  / 1200/1300

  +
  / 0900/1000
  / 1100/1200

gives the output: ::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1000/1100
  BFS/BRS 1200/1300

  2024-01-02
  BRS/BFS 0900/1000
  BFS/BRS 1100/1200


Night
-----

Updates eFJ with calculated night duration and, where necessary, night landing.

::

   efj night < input > output

The input: ::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

gives the ouput: ::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 n:20 ln
  BFS/BRS 1800/1900 n

If night duration is already recorded for any sector, that sector is not
updated.


VFR
---

Adds a flag to every sector to indicate that it was flown under visual flight rules.

::

   efj vfr < input > output

The input: ::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700
  BFS/BRS 1800/1900

gives the output: ::

  2024-01-01
  G-ABCD:A320
  BRS/BFS 1600/1700 v
  BFS/BRS 1800/1900 v
