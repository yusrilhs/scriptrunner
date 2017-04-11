Sublime Plugin Script Runner
============================

Run your script without move into command line.

Plugin for Sublime Text 3 for run your script from text editor. Doing it manually gets overly tedious sometimes so I wrote this plugin, cheers!

Installing:
-----------
**Without Git:** Download the latest source from [GitHub](https://github.com/yusrilhs/scriptrunner/archive/master.zip). Copy the whole directory into the Packages directory.

**With Git:** Clone the repository in your Sublime Text Packages directory:

    git clone git://github.com/yusrilhs/scriptrunner.git

The "Packages" packages directory is located at:

* OS X::

    ~/Library/Application Support/Sublime Text 3/Packages/

* Linux::

    ~/.Sublime Text 3/Packages/

* Windows::

    %APPDATA%/Sublime Text 3/Packages/

How to use
-----------
You can find at `Tools > Run Script` or you can use shortcut `shift+alt+b`

Configuration
--------------
You can find the configuration at `Tools > Run Script Configuration`, then add extensions and command to run your script.

Example:
```javascript
{
  // {scriptname} is for filename to execute, that's not required
  // that can be like: uglifyjs {scriptname} -o {scriptname}.js
  ".py": "python {scriptname}",

  // If you want execute the main file
  // Just add this two lines
  "main_file": "main.py",
  "main_dir": "/home/itsme/however"
}
```

If the `main_file` or `main_dir` is not defined this will be execute a file opened on the text editor.

