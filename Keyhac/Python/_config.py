
def configure(keymap):

    # Replacing Right-Shift key with BackSpace
    keymap.replaceKey( "RShift", "Back" )

    # Global keymap which affects any windows
    keymap_global = keymap.defineWindowKeymap()

    # Fn-A : Sample of assigning callable object to key
    def command_HelloWorld():
        print("Hello World!")

    keymap_global["Fn-A"] = command_HelloWorld


    # Fn-M : Zoom window (Test of UIElement.performAction)
    def command_ZoomWindow():

        elm = keymap.getFocusedUIElement()

        while elm:
            role = elm.getAttributeValue("AXRole")
            if role=="AXWindow":
                break
            elm = elm.getAttributeValue("AXParent")

        if elm:
            names = elm.getAttributeNames()
            if "AXZoomButton" in names:
                elm = elm.getAttributeValue("AXZoomButton")
                actions = elm.getActionNames()
                print(actions)
                elm.performAction("AXPress")

    keymap_global["Fn-M"] = command_ZoomWindow


    # Keymap for Xcode
    keymap_xcode = keymap.defineWindowKeymap( focus_path_pattern=r"AXApplication(Xcode):::*:::AXTextArea(None)" )

    # Fn-L : Select whole line
    keymap_xcode["Fn-L"] = "Cmd-Left", "Cmd-Left", "Shift-Cmd-Right"

    # Fn-A : Sample of assigning callable object to key
    def command_HelloXcode():
        print("Hello Xcode!")

    keymap_xcode["Fn-B"] = command_HelloXcode

    # Test of multi-stroke key binding
    keymap_xcode["Ctrl-X"] = keymap.defineMultiStrokeKeymap("Ctrl-X")
    keymap_xcode["Ctrl-X"]["Ctrl-O"] = "Cmd-O"
