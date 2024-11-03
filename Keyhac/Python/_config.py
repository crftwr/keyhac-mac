import sys
import keyhac

def configure(keymap):

    # Replacing Right-Shift key with BackSpace
    keymap.replace_key( "RShift", "Back" )

    # Defining user defined modifier keys
    keymap.define_modifier( "RCmd", "RUser0" )
    keymap.define_modifier( "RAlt", "RUser1" )

    # Global keymap which affects any windows
    keytable_global = keymap.define_keytable(focus_path_pattern="*")

    # Fn-A : Sample of assigning callable object to key
    def hello_world():
        print("Hello World!")

    keytable_global["Fn-A"] = hello_world

    # Fn-M : Zoom window (Test of UIElement.performAction)
    def zoom_window():

        elm = keymap.focus

        while elm:
            role = elm.getAttributeValue("AXRole")
            if role=="AXWindow":
                break
            elm = elm.getAttributeValue("AXParent")

        if elm:
            names = elm.getAttributeNames()
            if "AXZoomButton" in names:
                elm = elm.getAttributeValue("AXZoomButton")
                if elm:
                    actions = elm.getActionNames()
                    print(actions)
                    elm.performAction("AXPress")

    keytable_global["Fn-M"] = zoom_window


    # User0-Left/Right/Up/Down : Move current active window
    class MoveWindow:
        def __init__(self, x, y):
            self.x = x
            self.y = y

        def __call__(self):

            elm = keymap.focus

            while elm:
                role = elm.getAttributeValue("AXRole")
                if role=="AXWindow":
                    break
                elm = elm.getAttributeValue("AXParent")

            if elm:
                names = elm.getAttributeNames()
                pos = elm.getAttributeValue("AXPosition")
                pos[0] += self.x
                pos[1] += self.y
                elm.setAttributeValue("AXPosition", "point", pos)

    keytable_global["User0-Left"]  = MoveWindow(-10,0)
    keytable_global["User0-Right"] = MoveWindow(+10,0)
    keytable_global["User0-Up"]    = MoveWindow(0,-10)
    keytable_global["User0-Down"]  = MoveWindow(0,+10)


    # U0-A : Sample of assigning callable object to key
    def hello_user_modifier():
        print("Hello User Modifier!")

    keytable_global["RUser0-A"] = hello_user_modifier



    # Keymap for Xcode
    keytable_xcode = keymap.define_keytable( focus_path_pattern="/AXApplication(Xcode)/*/AXTextArea()" )

    # Fn-L : Select whole line
    keytable_xcode["Fn-L"] = "Cmd-Left", "Cmd-Left", "Shift-Cmd-Right"

    # Fn-A : Sample of assigning callable object to key
    def hello_xcode():
        print("Hello Xcode!")

    keytable_xcode["Fn-B"] = hello_xcode

    # Test of multi-stroke key binding
    keytable_xcode["Ctrl-X"] = keymap.define_keytable(name="Ctrl-X")
    keytable_xcode["Ctrl-X"]["Ctrl-O"] = "Cmd-O"
