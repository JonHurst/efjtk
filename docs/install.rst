Installation
============

Web Application
---------------

The toolkit is hooked up to a web application at https://hursts.org.uk/efj. No
installation is required to use this, just a reasonably modern web browser.

Local Install
-------------

Local installation provides greater flexibility and a slicker experience. It
also removes reliance on the continued provision of the web application.

A Python interpreter with version 3.11 or newer is required to run the tools
locally.

For Linux users, this will almost certainly be pre-installed. The graphical
interface uses the tkinter module, which some distributions don't install by
default; you may need to install this with your package manager if you wish
to use the graphical interface.

Windows users can install a Python Interpreter using the Microsoft Store -- just
search for "Python" and ensure the provider is the Python Software Foundation.

Mac users should visit https://www.python.org to download an installer.

Installation with pip
^^^^^^^^^^^^^^^^^^^^^

If you are familiar with pip, efjtk is available from PyPi. Install with your
favourite variation of::

  pip install efjtk

This installs two entry points, ``efj`` for command line use and ``efjgui`` to
run the graphical interface. Note pip’s warning to adjust your PATH
environmental variable if installing on Windows with the Microsoft Store version
of the Python interpreter.

Single file install
^^^^^^^^^^^^^^^^^^^

The graphical interface can be installed by downloading
https://hursts.org.uk/shiv/efjgui.pyw and copying to a location of your
choosing.

Windows users can just double click on this to run it. Linux and Mac users need
to set the executable permission on the file and can then run it as they would
any other script.

Uninstalling just requires deleting the file and deleting the files ``.efjtkrc``
and ``.efjtkguirc`` from your home/user directory if they exist. You can also
delete the cache directory, ``.shiv`` at any time — this is also found in your
home/user directory and is used to reduce startup time.
