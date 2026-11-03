# Scrap-Computers-File-Synchroniser
A script that goes along with the [mod](https://steamcommunity.com/sharedfiles/filedetails/?id=3757108567) that synchroniser the SC filesystem and a windows directory.
To use this, you must be running the game with the mod installed and with the block placed. I plan to eventually if I feel like it make it connect to computer you connect it to, but that's beyond my understanding of SM modding.

It can be run from the terminal with 2 args, The Computer ID, and the target path you want to work from

If you dont run it from the terminal or dont parse in the 2 args required, it will request them via input()

Note: Except from on start up, it only syncs from your OS's filesystem to the SC's filesystem, It is NOT TWO WAY. Any changes will be overwritten by the script when a file is moddified.
