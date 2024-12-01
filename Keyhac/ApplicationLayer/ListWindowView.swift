//
//  ListWindowView.swift
//  Keyhac
//
//  Created by Tomonori Shimomura on 2024-11-28.
//

import SwiftUI
import AppKit
import Cocoa

struct ListWindowView: View {
    
    struct Item {
        let icon: String
        let text: String
        let uuid: String
    }

    struct AttributedItem: Hashable {
        let icon: String
        let attrText: AttributedString
        let uuid: String
        let renderId: String = UUID().uuidString
        
        func hash(into hasher: inout Hasher) {
            hasher.combine(uuid)
        }
    }

    let items = [
        Item(icon: "👤", text: "Holly", uuid: UUID().uuidString),
        Item(icon: "👤", text: "Josh", uuid: UUID().uuidString),
        Item(icon: "👤", text: "Rhonda", uuid: UUID().uuidString),
        Item(icon: "👤", text: "Ted", uuid: UUID().uuidString),
        Item(icon: "📋", text: "Item001", uuid: UUID().uuidString),
        Item(icon: "📋", text: "Item002", uuid: UUID().uuidString),
        Item(icon: "📋", text: "Item003", uuid: UUID().uuidString),
        Item(icon: "📋", text: "Item004", uuid: UUID().uuidString),
    ]
    
    @State private var searchText = ""
    @State private var focusedListItem: Int = 0
    @State private var scrollPosition = ScrollPosition(edge: .top)
    
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
                    onKeyDown: self.onKeyDown
                )
            }
            .offset(x: 0, y: 2)
            
            ScrollView {
                LazyVStack {
                    let searchResults = self.searchResults

                    ForEach(Array(searchResults.enumerated()), id: \.element) { index, item in
                        
                        let focused = focusedListItem == index

                        HStack {
                            Text(item.icon)
                                .font(.system(size: 8))
                                .frame(width: 12)
                                .foregroundStyle(.opacity(0.5))
                            
                            Text(item.attrText)
                            
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
    
    func onKeyDown(_ key: CustomTextFieldView.Key) {
        switch key {
        case .up:
            let searchResults = self.searchResults
            
            focusedListItem = max(focusedListItem-1, 0)
            if focusedListItem < searchResults.count {
                scrollPosition.scrollTo(id: searchResults[focusedListItem].uuid, anchor: .top)
            }
            else {
                scrollPosition.scrollTo(edge: .top)
            }
            
        case .down:
            let searchResults = self.searchResults
            
            focusedListItem = max(min(focusedListItem+1, searchResults.count-1), 0)
            if focusedListItem < searchResults.count {
                scrollPosition.scrollTo(id: searchResults[focusedListItem].uuid, anchor: .bottom)
            }
            else {
                scrollPosition.scrollTo(edge: .top)
            }
            
        default:
            break
        }
    }
    
    var searchResults: [AttributedItem] {
        
        let trimmedString = self.searchText.trimmingCharacters(in: .whitespacesAndNewlines)
        let words = trimmedString.components(separatedBy: " ")
        
        let filteredItems = self.items.filter {
            for word in words {
                if word.isEmpty {
                    continue
                }
                if $0.text.range(of: word, options: .caseInsensitive) == nil {
                    return false
                }
            }
            return true
        }
        
        let attributedItems = filteredItems.map {
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
        return attributedItems
    }
}

struct CustomTextFieldView: NSViewRepresentable {
    
    enum Key {
        case tab
        case enter
        case escape
        case up
        case down
    }

    @Binding var stringValue: String
    var placeholder: String
    var autoFocus = false
    var onChange: (() -> Void)?
    var onKeyDown: ((Key) -> Void)?
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
            parent.stringValue = textField.stringValue
            parent.onChange?()
        }
        
        func control(_ control: NSControl, textView: NSTextView, doCommandBy commandSelector: Selector) -> Bool {
            
            if commandSelector == #selector(NSStandardKeyBindingResponding.insertTab(_:)) {
                parent.onKeyDown?(.tab)
                return true
            }
            else if commandSelector == #selector(NSStandardKeyBindingResponding.insertNewline(_:)) {
                parent.onKeyDown?(.enter)
                return true
            }
            else if commandSelector == #selector(NSStandardKeyBindingResponding.cancelOperation(_:)) {
                parent.onKeyDown?(.escape)
                return true
            }
            else if commandSelector == #selector(NSStandardKeyBindingResponding.moveUp(_:)) {
                parent.onKeyDown?(.up)
                return true
            }
            else if commandSelector == #selector(NSStandardKeyBindingResponding.moveDown(_:)) {
                parent.onKeyDown?(.down)
                return true
            }

            return false
        }
    }
}
