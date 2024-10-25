
def configure(keymap):

    # Replacing Right-Shift key with BackSpace
    keymap.replaceKey( "RShift", "Back" )

    # Global keymap which affects any windows
    keymap_global = keymap.defineWindowKeymap()

    # Fn-A : Sample of assigning callable object to key
    def command_HelloWorld():
        print("Hello World!")

    keymap_global["Fn-A"] = command_HelloWorld


    # Keymap for Xcode
    keymap_xcode = keymap.defineWindowKeymap( focus_path_pattern=r"AXApplication(Xcode):::*" )

    # Fn-A : Sample of assigning callable object to key
    def command_HelloXcode():
        print("Hello Xcode!")

    keymap_xcode["Fn-B"] = command_HelloXcode

    # Test of multi-stroke key binding
    keymap_xcode["Ctrl-X"] = keymap.defineMultiStrokeKeymap("Ctrl-X")
    keymap_xcode["Ctrl-X"]["Ctrl-O"] = "Cmd-O"
