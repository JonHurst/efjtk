Overview
========

This is a set of tools for working with electronic Flight Journal (eFJ) files.
An eFJ file is just a text file that stores personal flight data using a simple,
intuitive scheme that is easy to work with for both humans and computers. A full
description of the scheme can be found at
https://hursts.org.uk/efjdocs/format.html.

Three interfaces are provided: a :ref:`web application<webapp>`, a :ref:`Tk
based graphical user interface<gui>` and a :ref:`command line
interface<command_line>`.

The tools fall into two categories: tools to convert an eFJ into other useful
formats and tools to modify an eFJ.

The former category includes the ability to generate an `FCL.050 compliant
logbook
<https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_
and a set of summary tables, both as simple, standalone HTML files that can be
viewed in any web browser or processed further using spreadsheets, word
processors, PDF converters etc.

The latter category provides things like regulatory night flying calculation and
quick flagging of roles for First Officers.
