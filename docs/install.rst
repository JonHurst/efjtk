Installation
============

Web Interface
-------------

The web interface is available by visiting `https://hursts.org.uk/efj </efj/>`_
with a reasonably modern web browser. The application will run on a remote
server, so no installation is required. The interface is somewhat clunky
compared to those available by installing locally (for security reasons, working
with local files in a web browser is awkward), but all the important features
are available.

Local Install
-------------

The application is distributed as a single, small (~300KB), file. This file does
not require installation. Backing up the application is just a matter of copying
the downloaded file to somewhere safe. Uninstall is by deleting the file.

The file is a `Python zipapp <https://docs.python.org/3/library/zipapp.html>`_,
which behaves exactly like a single file Python script. This means that you need
to have a Python interpreter (version 3.11 or newer) installed on your system to
run it. The benefit of this complication is that it makes the application cross
platform and future proof: you will continue being able to run the file you
downloaded for as long as a Python interpreter is available on your platform of
choice. With the prevalence of Python in academia and industry, this is about as
future proof as it is possible to get.

For Linux users, version 3.11 or newer of the Python interpreter will almost
certainly be pre-installed. The graphical interface uses the tkinter module,
which some distributions don't install by default; if you wish to use it, you
may need to install the module with your package manager (it is ``python3-tk``
on Debian/Ubuntu).

Windows users can install a suitable Python Interpreter using the Microsoft
Store -- just search for "Python" and ensure the provider is the Python Software
Foundation.

Mac users should visit https://docs.python.org/3/using/mac.html for
straightforward instructions on how to install.

For downloading the application file, there are two options. Most users should
download `efjgui.pyw </shiv/efjgui.pyw>`_, which gives you the graphical
interface. Advanced users can download `efj.py </shiv/efj.py>`_, which gives you
the command line interface. These links will always point to the most up to date
version. Note that the ``gui`` command line option allows the graphical
interface to be started from the command line interface.

Move the downloaded file to wherever you feel is appropriate — it can be run
from anywhere. Windows users can just double click it to run it. Linux users
need to set the executable permission on the file and can then run it as they
would any other executable. Mac users can do the same as Linux users, or they
can look at the instructions mentioned above to use the Finder.

The first time the application is run it will create a directory named ``.shiv``
in your home directory. This is just a cache that improves startup times, so
feel free to delete it — it will be created afresh next time the application runs.
