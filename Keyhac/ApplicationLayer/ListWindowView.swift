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
    
    let names = ["Holly", "Josh", "Rhonda", "Ted", "Item001", "Item002", "Item003", "Item004"]
    
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
                    tag: 1
                )
            }
            .offset(x: 0, y: 2)
            
            ScrollView {
                LazyVStack {
                    let searchResults = self.searchResults
                    
                    ForEach(Array(searchResults.enumerated()), id: \.element) { index, name in
                        
                        let focused = focusedListItem == index
                        
                        HStack {
                            Text("📋")
                                .font(.system(size: 8))
                                .frame(width: 12)
                                .foregroundStyle(.opacity(0.5))
                            
                            Text(name)
                            
                            Spacer()
                        }
                        .id(name)
                        .background(focused ? Color.blue.opacity(0.3) : Color.clear)
                    }
                }
                .padding(.all, 8)
            }
            .background(Color.white)
            //        .focusable()
            //        .focused($focusedField, equals: .list)
            .scrollPosition($scrollPosition)
        }
        .frame(minWidth: 200, idealWidth: 200, maxWidth: 500, minHeight: 32, idealHeight: 32, maxHeight: 500, alignment: .top)
        .padding(.all, 4)
    }
    
    var searchResults: [AttributedString] {
        if searchText.isEmpty {
            let filteredNames = names
            let attributedNames = filteredNames.map {
                // FIXME: escape
                try! AttributedString(markdown: $0)
            }
            return attributedNames
        } else {
            let filteredNames = names.filter { $0.contains(searchText) }
            let attributedNames = filteredNames.map {
                // FIXME: escape
                try! AttributedString(markdown: $0.replacingOccurrences(of: searchText, with: String(format: "**%@**", searchText) ))
            }
            return attributedNames
        }
    }
}
