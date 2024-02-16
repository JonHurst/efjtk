Overview
========

This is a set of tools for working with electronic Flight Journal (eFJ) files.
These are simple text files for recording personal flight data. They have a
formalised scheme that allows both humans and computers to easily work with
them. A full description can be found at
https://hursts.org.uk/efjdocs/format.html.

The tools fall into two categories: tools to modify an eFJ file and tools to
convert one into other useful formats. The latter category includes the ability
to generate an FCL.050 compliant logbook and summary tables as standalone HTML
files.

All the tools are filters, i.e. they acquire data from stdin, output results to
stdout and send error messages to stdout. This is particularly useful when
using a reasonably competent text editor which can use such filters to process
selected regions.
