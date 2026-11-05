---
name: swift-dev
description: "Swift development. Use for Swift, SwiftUI, UIKit, Vapor, SPM, XCTest, Combine."
user-invocable: true
allowed-tools: Glob, Read, Grep, Bash, Task, Skill, Edit, Write, EnterPlanMode
---

# Swift Development

**Announce:** "I'm using the swift-dev skill."

Follow the [development loop](../../shared/development-loop.md). Read [patterns.md](patterns.md) before changing code.

---

## Swift-Specific Configuration

### Verification Commands

**SPM projects:**
- `swift build` — compilation
- `swift test` — tests
- `swiftlint` — linting (if configured)
- Coverage target: 70-80%

**Xcode projects:**
- `xcodebuild build` or `xcodebuild test`
- SwiftUI: `xcodebuild build -scheme [scheme] -destination 'platform=iOS Simulator,name=iPhone 16'`

### Implementation Rules

- **Model structure** — Structs with Codable CRUD variants per entity (CreateRequest/UpdateRequest/Response), domain-driven file organization, composition over deep inheritance, prefer structs over classes
- **Minimize complexity** — lazy sequences for large collections, Dictionary lookups over array scans
- **Preserve compatibility** — CodingKeys for renamed fields, default values for new properties, preserve public API signatures, @available for deprecations

### Staff Review Configuration

- **Patterns file path:** Path to this skill's `patterns.md`

---

## Swift-Specific Rules

- The compiler catches type errors, not logic bugs or architectural problems — verification is still mandatory
- SwiftUI previews only prove the view compiles — run `swift test` for real verification
- No positive claim without running `swift test` or `swift build`

---

## Quality Checklist (Swift-Specific)

Check these before reporting the work as done:

- [ ] Using Swift 5.9+ / Swift 6 features where appropriate
- [ ] Structs preferred over classes (value semantics by default)
- [ ] Protocol-oriented design used
- [ ] async/await for asynchronous code
- [ ] No force unwraps outside tests
- [ ] Proper error handling with typed throws or do/catch
- [ ] `swift build` succeeds without warnings
- [ ] `swift test` passes (or `xcodebuild test`)
- [ ] `swiftlint` passes (if configured)
