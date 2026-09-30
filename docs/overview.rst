Overview
========

This is a set of tools for working with electronic Flight Journal (eFJ) files.
An eFJ file is just a text file that stores personal flight data using `a
simple, intuitive schema <https://hursts.org.uk/efjdocs/format.html>`_ which is
designed to be quick and easy to work with for both humans and computers.

Three interfaces are provided: a primary :ref:`Tk based graphical user
interface<gui>`, providing a one stop shop for working with eFJ files, a
:ref:`command line interface<command_line>` suitable for simple scripting and/or
incorporating eFJ processing functionality into your favored text editor, and a
:ref:`web interface<webapp>`, which, while more limited than the other two
interfaces, allows the toolkit to be used without needing to install anything
locally.

Two categories of tools are provided: tools to modify an eFJ in place and tools
to convert an eFJ into standalone HTML files which can then be opened in any
browser or imported into any spreadsheet.

The first category includes a tool to calculate regulatory night hours, which is
very difficult to calculate by hand, and a tool to expand the extremely terse
format used for minimum effort data entry into the more readable long form.

The second category includes a tool to export a logbook in a format that is
`compliant with EASA's acceptable means of compliance
<https://www.easa.europa.eu/en/document-library/easy-access-rules/online-publications/easy-access-rules-aircrew-regulation-eu-no?page=5#_Toc522628396>`_,
(which has also been adopted by the UK CAA), and a tool to export a Summary of
Flying for any desired period.
