# FileSysArchive

This app will archive items to file system directory and restore items from there as well.

Note: This functionality is included in core Portal. This repository serves as an example for developing an 
Archive Framework plugin.

You can run this plugin as such along the standard Portal filesys plugin for testing.

The example uses same roles as the Portal filesys archive.

If you build your own archive plugin based on this example, please make sure to
replace the following UUIDs with new random ones to not collide with the example:

    41E00013-517F-4D7C-AAC3-66EE75A203AE
    A56E3B15-9794-481B-A5AF-0A355325EA2A
    B85C1D2A-68BF-4BFA-BFD6-8818237744A5
    F137BBBE-E64D-4A31-B1F8-9DD9037A3E50

## Prerequisites

This plugin requires Portal 4.1.6 or later.

## Installation

To install this plugin, copy the contents of this directory to `/opt/cantemo/portal/portal/plugins/filesysarchive_example`,
make sure the directory is readable by the Portal web-worker (`www-data`).

For example - on a Portal system run the following commands

    curl -L https://github.com/Cantemo/filesysarchive/archive/master.zip > filesysarchive_example.zip

    unzip filesysarchive_example.zip

    mv filesysarchive-master /opt/cantemo/portal/portal/plugins/filesysarchive_example
    
    chown -R www-data:www-data /opt/cantemo/portal/portal/plugins/filesysarchive_example
    
    sudo systemctl restart portal-web

After this:

* Run database migration to create the settings table
    * `/opt/cantemo/portal/manage.py migrate filesysarchive_example`
* On the Portal system, enable the plugin
    * Open **System > System Overview**
    * Locate the "FileSysArchive Example" plugin and click on the selector to enable it
    * Restart all Portal services: `sudo systemctl restart portal.target`
    * Now you should
        * see a link to the plugin settings at **System > Archive Framework > FileSysArchive Example**
        * be able to archive items with **FileSysArchive Example**
 
