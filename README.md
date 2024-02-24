# eFJ Toolkit #

An electronic Flight Journal (eFJ) is just a text file containing personal
flight data using a simple, intuitive scheme that is easy for both computers
and humans to work with. It looks something like this:

      2024-02-04
      G-EZBY:A319
      BRS/GLA 0702/0818 n:18 m
      GLA/BHX 0848/1037  # Diversion due weather
      BHX/BRS 1300/1341

      2024-02-05
      G-UZHI:A320
      BRS/FNC 0708/1045 n:6
      FNC/BRS 1127/1451 m

Full details of the format may be found at <https://hursts.org.uk/efjdocs/format.html>.

This is a set of tools for working with text files following this scheme. It
includes the ability to create FCL.050 compliant logbooks and summaries as
simple, standalone HTML files that can be viewed with any web browser and
further processed with spreadsheets, word processors, PDF converters etc. Full
documentation is available at <https://hursts.org.uk/efjtkdocs>.

The tools are written as command line filters, but a simple GUI front end is
also provided for those that prefer. The tools are also available hooked up to
a web application at <https://hursts.org.uk/efj> if you prefer not to install
locally.
