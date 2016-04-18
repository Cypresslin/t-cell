# T-Cell
T-Cell is a component issue lookup tool that helps you to find known bugs on your Ubuntu.

It will help you to check these things:
  - PCI devices
  - USB devices
  - PNP devices
  - Input devices
  - User-space related issues

The goal for this tool is to allow users to be aware of potential bugs they might encounter while testing with a Live-USB, especially pre-installed Ubuntu users. To prevent some "not working after re-install" tragedies.

### Usage
Download the tar ball first, let's say it's now in your ~/Download directory, and simply run:

       $ tar -zxvf t-cell.tar.gz
       $ ./RunMe.py
       Your distro: precise
       Your kernel version: 3.13.X 
       Checking touchpad/mouse
       Scanning components...
       Loading database...
       Running component check...
       Known issue for input-0002:0008: http://pad.lv/1337199 (Touchpad)
       Known issue for pnp-SMO8810: http://pad.lv/1199217 (Accelerometer)
       Checking common issues...
       Known issue for precise: http://pad.lv/1218810 (Hotkeys)

You will be able to see the detected known issues to your system.

Please note that since it just acts like a T-lymphocytes ([memory-T cell], that's how this tool get its name :D), if a bug has never been reported or collected before, it will know nothing about it.
So if you have a launchpad bug report to a specific hardware component, please feel free to update it.

### Development

Please feel free to take part in this project. You will be able to fetch the source code from:
 - https://launchpad.net/t-cell
 - https://github.com/Cypresslin/t-cell

You can also open a bug report on the t-cell project page (or github, as you wish) to open a request for updating the database, you will need to provide the following information:
 - PCI / USB or any other unique ID for the device (if applicable).
 - Link to the bug report of that device.

*Note that please only escalate the bug for stock image.*

License
----

GNU GPL v3 

[memory-T cell]:https://en.wikipedia.org/wiki/Memory_T_cell
