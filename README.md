# eFJ Toolkit #

An electronic Flight Journal (eFJ) is a text file used for recording personal
flight data using a intuitive formalised scheme. It looks something like this:

      2024-02-04
      G-EZBY:A319
      BRS/GLA 0702/0818 n:18 m
      GLA/BHX 0848/1037  # Diversion due weather
      BHX/BRS 1300/1341

      2024-02-05
      G-UZHI:A320
      BRS/FNC 0708/1045 n:6
      FNC/BRS 1127/1451 m

Full details may be found at <https://hursts.org.uk/efjdocs/format.html>.

This toolkit either processes the eFJ into other forms, such as an HTML FCL.050
compliant logbook, or modifies the eFJ in some useful way. It is written as a
(filter)[filter](https://en.wikipedia.org/wiki/Filter_(software)) for maximum
flexibility.

## FCL.050 logbok ##

To create an HTML logbook, each aircraft type needs to be specified as either
single pilot, single engine; single pilot, multi engine; or multi-crew. This is
handled with a configuration file. A template for this file where all types are
specified as single pilot, single engine can be created with:

    efj config < my_efj > my_config

This file should be edited, replacing `spse` with `spme` or `mc` where
appropriate. The logbook can then be created with:

    efj logbook -c my_config < my_efj > my_logbook.html

The `-c` option can be omitted if the config file is stored as `~/.efjrc` or
`~/.config/efjrc` for Unix/Mac of `.efjrc` in your home directory on Windows.

The created HTML file is standalone, so can be easily moved around and opened
with any modern browser. It can also be imported into spreadsheets and word
processors.

## Summary ##
