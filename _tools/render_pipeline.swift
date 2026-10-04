// Renders the sample photos through the app's own StudioPipeline package, on every background.
// Build: swiftc -O -swift-version 6 -enable-upcoming-feature NonisolatedNonsendingByDefault \
//   -enable-upcoming-feature InferIsolatedConformances -enable-upcoming-feature MemberImportVisibility \
//   -o driver ~/Developer/ShelfReady/StudioPipeline/Sources/StudioPipeline/*.swift main.swift
// Run on macOS (Vision segmentation does not work in the Simulator): ./driver IN_DIR OUT_DIR

import Foundation
import CoreImage
let args = CommandLine.arguments
let inDir = URL(fileURLWithPath: args[1]); let outDir = URL(fileURLWithPath: args[2])
let files = try FileManager.default.contentsOfDirectory(atPath: inDir.path).sorted()
let presets: [StudioPreset] = StudioPreset.all + StudioPalette.colours
for f in files {
    let data = try Data(contentsOf: inDir.appendingPathComponent(f))
    let prepared = try await PreparedPhoto.prepare(imageData: data)
    let base = (f as NSString).deletingPathExtension
    for p in presets {
        let out = try await prepared.render(preset: p)
        try out.write(to: outDir.appendingPathComponent("\(base)__\(p.id).bin"))
    }
    print(base, prepared.subjectCount)
}
