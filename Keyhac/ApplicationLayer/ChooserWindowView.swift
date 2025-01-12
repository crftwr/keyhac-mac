//
//  ChooserWindowView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-11-28.
//

import SwiftUI
import AppKit
import Cocoa

struct ChooserWindowView: View {
    
    @Environment(\.dismissWindow) private var dismissWindow
    @Environment(\.controlActiveState) private var controlActiveState

    private struct AttributedItem: Hashable {
        let icon: String
        let attrText: AttributedString
        let uuid: String
        let renderId: String = UUID().uuidString
        
        func hash(into hasher: inout Hasher) {
            hasher.combine(uuid)
        }
    }
    
    @State private var chooserName: String = ""

    @State private var searchText = ""
    @State private var selectedIndex: Int = 0
    @State private var selectedUuid: String = ""
    @State private var scrollPosition = ScrollPosition(edge: .top)
    @State private var searchResults: [AttributedItem] = []
    
    var body: some View {
        VStack {
            HStack {
                Image("Search")
                    .imageScale(.medium)
                    .frame(width: 16, height: 8, alignment: .center)
                    .offset(x: 3, y: 1)
                
                CustomTextFieldView(
                    stringValue: $searchText,
                    placeholder: "Search",
                    autoFocus: true,
                    onChange: self.onSearchTextChange,
                    onKeyDown: self.onKeyDown
                )
                .onChange(of: controlActiveState) { oldValue, newValue in
                    // Close window when deactivated
                    if newValue == .inactive {
                        dismissWindow(id: "chooser")
                    }
                }
                .onOpenURL { url in
                    
                    // extract chooser name from the URL
                    let path = url.path
                    if path.starts(with: "/") {
                        let begin = path.index(path.startIndex, offsetBy: 1)
                        let end = path.index(path.endIndex, offsetBy: 0)
                        chooserName = String(path[begin..<end])
                    }
                    
                    // extract desired window center position from the query parameters
                    var x :CGFloat = 0
                    var y :CGFloat = 0
                    var width :CGFloat = 0
                    var height :CGFloat = 0
                    let q = url.query(percentEncoded: true)
                    if let q {
                        q.split(separator: "&").forEach { param in
                            let keyValue = param.split(separator: "=")
                            if keyValue.count == 2 {
                                let key = String(keyValue[0])
                                let value = String(keyValue[1])
                                
                                switch key {
                                case "x":
                                    let value = Double(value)
                                    if let value { x = value }
                                case "y":
                                    let value = Double(value)
                                    if let value { y = value }
                                case "width":
                                    let value = Double(value)
                                    if let value { width = value }
                                case "height":
                                    let value = Double(value)
                                    if let value { height = value }
                                default:
                                    break
                                }
                            }
                        }
                    }
                    
                    // set Chooser window position
                    let window = NSApplication.shared.windows.first { $0.title == "Keyhac Chooser" }
                    if let window {
                        
                        let mainScreenFrame = NSScreen.main?.frame
                        if let mainScreenFrame {
                            let position = NSPoint(
                                x: x + width/2 - window.frame.width/2,
                                y: mainScreenFrame.height - (y + height/2 - window.frame.height/2)
                            )
                            window.setFrameTopLeftPoint(position)
                        }
                    }
                    
                    searchText = ""
                    selectedIndex = 0
                    selectedUuid = ""
                    scrollPosition = ScrollPosition(edge: .top)
                    searchResults = []
                    
                    self.onSearchTextChange()
                }
            }
            .offset(x: 0, y: 2)
            
            ScrollView {
                LazyVStack {
                    ForEach(Array(searchResults.enumerated()), id: \.element) { index, item in
                        
                        let focused = selectedIndex == index

                        HStack {
                            Text(item.icon)
                                .font(.system(size: 8))
                                .lineLimit(1)
                                .frame(width: 12)
                                .foregroundStyle(.opacity(0.5))
                            
                            Text(item.attrText)
                                .lineLimit(1)

                            Spacer()
                        }
                        .id(item.renderId)
                        .background(focused ? Color.blue.opacity(0.3) : Color.clear)
                    }
                }
                .padding(.all, 8)
            }
            .background(Color.white)
            .scrollPosition($scrollPosition)
        }
        .frame(minWidth: 200, idealWidth: 200, maxWidth: 500, minHeight: 32, idealHeight: 32, maxHeight: 500, alignment: .top)
        .padding(.all, 4)
    }
    
    func onSearchTextChange() {
        
        guard let chooser = Chooser.getInstance(name: self.chooserName) else {
            return
        }

        let trimmedString = self.searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        let words = trimmedString.components(separatedBy: " ")

        // Select the first item by default
        selectedIndex = 0
        
        var index = 0
        let filteredItems = chooser.items.filter {
            
            for word in words {
                if word.isEmpty {
                    continue
                }
                if $0.text.range(of: word, options: .caseInsensitive) == nil {
                    return false
                }
            }
            
            // Keep item selection by UUID
            if $0.uuid == selectedUuid {
                selectedIndex = index
            }
            index += 1
            
            return true
        }
        
        self.searchResults = filteredItems.map {
            var attrString = AttributedString($0.text)
            for word in words {
                if word.isEmpty {
                    continue
                }
                if let range = attrString.range(of: word, options: .caseInsensitive) {
                    print("Underline range: \(range)")
                    attrString[range].underlineStyle = Text.LineStyle(pattern: .solid, color: .gray)
                }
            }
            return AttributedItem(icon: $0.icon, attrText: attrString, uuid: $0.uuid)
        }
        
        if selectedIndex < searchResults.count {
            scrollPosition.scrollTo(id: searchResults[selectedIndex].renderId, anchor: .bottom)
            scrollPosition.scrollTo(id: searchResults[selectedIndex].renderId, anchor: .top)
        }
        else {
            scrollPosition.scrollTo(edge: .top)
        }
    }
    
    func onKeyDown(_ key: CustomTextFieldView.Key) -> Bool {
        
        let evt = NSApp.currentEvent
        guard let evt = evt else {return false}

        switch key {
        case .up:
            selectedIndex = max(selectedIndex-1, 0)
            if selectedIndex < searchResults.count {
                scrollPosition.scrollTo(id: searchResults[selectedIndex].renderId, anchor: .top)
            }
            else {
                scrollPosition.scrollTo(edge: .top)
            }
            selectedUuid = searchResults[selectedIndex].uuid
            
            return true
            
        case .down:
            selectedIndex = max(min(selectedIndex+1, searchResults.count-1), 0)
            if selectedIndex < searchResults.count {
                scrollPosition.scrollTo(id: searchResults[selectedIndex].renderId, anchor: .bottom)
            }
            else {
                scrollPosition.scrollTo(edge: .top)
            }
            selectedUuid = searchResults[selectedIndex].uuid
            
            return true

        case .enter:
            guard let chooser = Chooser.getInstance(name: self.chooserName) else { break }

            if selectedIndex < searchResults.count {
                chooser.onSelected(uuid: searchResults[selectedIndex].uuid, nsModifierFlags: evt.modifierFlags)
                
                dismissWindow(id: "chooser")
                
                return true
            }
            else {
                return false
            }

        case .escape:
            guard let chooser = Chooser.getInstance(name: self.chooserName) else { break }

            chooser.onCanceled()
            
            dismissWindow(id: "chooser")

            return true
        }
        
        return false
    }
}

struct CustomTextFieldView: NSViewRepresentable {
    
    enum Key {
        case enter
        case escape
        case up
        case down
    }

    @Binding var stringValue: String
    var placeholder: String
    var autoFocus = false
    var onChange: (() -> Void)?
    var onKeyDown: ((Key) -> Bool)?
    @State private var didFocus = false
    
    func makeNSView(context: Context) -> NSTextField {
        let textField = NSTextField()
        textField.stringValue = stringValue
        textField.placeholderString = placeholder
        textField.delegate = context.coordinator
        textField.alignment = .left
        textField.bezelStyle = .squareBezel
        return textField
    }
    
    func updateNSView(_ nsView: NSTextField, context: Context) {
        if autoFocus && !didFocus {
            // FIXME: mainWindow限定？
            NSApplication.shared.mainWindow?.perform(
                #selector(NSApplication.shared.mainWindow?.makeFirstResponder(_:)),
                with: nsView,
                afterDelay: 0.0
            )
            
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                didFocus = true
            }
        }
        
        if nsView.stringValue != stringValue {
            nsView.stringValue = stringValue
        }
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(with: self)
    }

    class Coordinator: NSObject, NSTextFieldDelegate {
        let parent: CustomTextFieldView
        
        init(with parent: CustomTextFieldView) {
            self.parent = parent
            super.init()
            
            NotificationCenter.default.addObserver(
                self,
                selector: #selector(handleAppDidBecomeActive(notification:)),
                name: NSApplication.didBecomeActiveNotification,
                object: nil)
        }
        
        @objc
        func handleAppDidBecomeActive(notification: Notification) {
            if parent.autoFocus && !parent.didFocus {
                DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
                    self.parent.didFocus = false
                }
            }
        }

        func controlTextDidChange(_ obj: Notification) {
            guard let textField = obj.object as? NSTextField else { return }
            textDidChange(textField.stringValue)
        }
        
        func textDidChange(_ text: String) {
            parent.stringValue = text
            parent.onChange?()
        }
        
        func control(_ control: NSControl, textView: NSTextView, doCommandBy commandSelector: Selector) -> Bool {
            
            let evt = NSApp.currentEvent
            guard let evt = evt else {return false}

            if evt.keyCode == 0x24 {
                if let onKeyDown = parent.onKeyDown {
                    return onKeyDown(.enter)
                }
                return false
            }
            else if commandSelector == #selector(NSStandardKeyBindingResponding.cancelOperation(_:)) {

                // If text is not empty, clear it instead of closing window
                if control.stringValue.count > 0 {
                    if let textField = control as? NSTextField {
                        textField.stringValue = ""
                        textDidChange(textField.stringValue)
                    }
                    return true
                }

                if let onKeyDown = parent.onKeyDown {
                    return onKeyDown(.escape)
                }

                return false
            }
            else if commandSelector == #selector(NSStandardKeyBindingResponding.moveUp(_:)) {

                if let onKeyDown = parent.onKeyDown {
                    return onKeyDown(.up)
                }

                return false
            }
            else if commandSelector == #selector(NSStandardKeyBindingResponding.moveDown(_:)) {

                if let onKeyDown = parent.onKeyDown {
                    return onKeyDown(.down)
                }

                return false
            }

            return false
        }
    }
}
