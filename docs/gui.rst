.. _gui:

Graphical User Interface
========================

A simple GUI application is provided as a front end to the command line tools.

When referencing the documentation, a command line of the form::

  $ efj action < input > output

will be presented when describing a tool. The GUI runs this for you. The action
is chosen from the top level menus and all the tools use the loaded text as the
input.

Tools that :ref:`modify an eFJ<Modification>`, found under the top level
'Modify' menu, modify the text in place, i.e. the input is overwritten by the
output. If any text is selected, only lines with selected text are updated.

Those tools that :ref:`convert the eFJ<Convert>` into new formats, found under
the 'Export' menu, create new files and do not change the input text.

A simple editor for the configuration file is included. If an attempt is made to
create an FCL.050 logbook with insufficient information regarding the class of
referenced aircraft types, this editor will pop up with the missing types
classified as ``spse`` (single pilot single engine). Simply change these to
``spme`` for single pilot multi engine operations or ``mc`` for multi-crew
operations. Syntax highlighting and validation are provided to help prevent
errors.
