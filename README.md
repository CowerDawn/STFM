# STFM

STFM - GNU simple terminal file manager for Unix-like system. It is made for the WM-IT window manager emulator.

Activate the SGFM.py script if you want your own file manager with a GUI.

# Dependencies:

ncurses, dirent.h, stdlib.h, string.h, unistd.h, sys/stat.h, sys/types.h, fcntl.h, errno.h, stdio.h, ctype.h


# Install:

`make`

`sudo make install`

# Controls


Arrow Up (↑): Moves the selection up in the file list.

Arrow Down (↓): Moves the selection down in the file list.

Enter: Opens the selected file or directory.

Backspace: Navigates to the parent directory.

Home: Navigates to the home directory.

Delete: Deletes the selected file or directory after confirmation.

Ctrl + N: Creates a new directory.

Ctrl + T: Creates a new text file.

Ctrl + E: Opens the selected text file in the default editor (nano).

Ctrl + O: Opens the selected file with the default application.

Ctrl + Q: Exits the file manager.

