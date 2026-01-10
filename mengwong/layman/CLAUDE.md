# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Layman is a React/Next.js application for interactive visualization of and/or trees (Boolean logic structures) used in legal rule representation. It is part of the L4 project ecosystem, which aims to formalize legal rules as executable specifications.

The app displays legal rules (legislation, contracts, insurance policies) as both textual sentences and interactive flowchart diagrams. Users can expand/collapse logical groupings to see different combinations of conditions in disjunctive normal form (DNF).

## Build and Run

```bash
npm install       # Install dependencies
npm run dev       # Development server at http://localhost:3000
npm run build     # Production build
npm run lint      # ESLint with --fix
```

## Architecture

### Core Data Model (`src/woon.ts`)

The `Vine` class hierarchy represents Boolean tree structures:

- **`Vine`** - Base class with expand/collapse state (`HideShow`) and methods for DNF expansion
- **`AnyAll`** - Abstract parent node class managing children
- **`Any`** - Disjunction (OR) - when expanded, shows each child as a parallel path
- **`All`** - Conjunction (AND) - children must all be satisfied in sequence
- **`Leaf`** - Terminal element with boolean value (clickable)
- **`Fill`** - Inert text for grammatical flow (e.g., "or", "and")
- **`Not`** - Negation wrapper

Key operations:
- `expand()` - Converts tree to DNF (array of arrays), respecting collapse state
- `getFlowNodes()` / `getFlowEdges()` - Generate ReactFlow diagram elements
- `clone()` - Deep copy for React state management

### Syntactic Sugar and Isomorphism

The DSL provides six constructor functions that afford isomorphic transformation between representations:

```typescript
// Structural combinators
all(...children)  → All    // Conjunction: A ∧ B ∧ C
any(...children)  → Any    // Disjunction: A ∨ B ∨ C
com(...children)  → All    // Compound sequence (alias for all, semantic clarity)
not(child)        → Not    // Negation: ¬A

// Terminal nodes
ele(text)         → Leaf   // Value term: ground term with boolean value (true/false/unknown)
say(text)         → Fill   // Filler: comment-like text for grammatical flow, logically inert
```

**Value Terms vs Filler:**

| | `ele()` / Leaf | `say()` / Fill |
|---|---|---|
| Purpose | Propositions to evaluate | Grammatical scaffolding |
| Boolean value | true / false / undefined | N/A |
| In DNF expansion | Included | Filtered out (connectives like "or") |
| In diagram | Clickable node (colored by value) | Transparent label |
| Example | `ele('born in UK')` | `say('or')`, `say('and')` |

**The Isomorphism Triangle:**

```
        DSL Source
       /          \
      /            \
     v              v
 Diagram  <---->  Sentences (DNF)
```

1. **DSL → AST**: Constructor functions build the `Vine` tree structure
2. **AST → DNF (Sentences)**: `expand()` converts to disjunctive normal form
3. **AST → Diagram**: `getFlowNodes()`/`getFlowEdges()` generate ReactFlow elements

**DNF Expansion Algorithm** (`src/woon.ts:8-26`):

The `expand()` method implements sum-of-products conversion:
- **OR (Any)**: Concatenates child expansions → `[[a], [b], [c]]`
- **AND (All)**: Takes cartesian product → `[[a, b, c]]`
- **Collapse state**: When collapsed, Any behaves like All (single grouped line)

The `xprod()` utility uses `_.product` (lodash) for cartesian product, enabling both operations.

**Grammatical Filler Handling** (`src/pages/docview.tsx:206-210`):

The `excludeFill0` filter removes logical connectives ("or", "either", "whether") from expanded sentences since they're implicit in the DNF structure:

```typescript
const excludeFill0 = {
  fParent: (s) => s instanceof All || (s instanceof Any && s.viz !== HideShow.Collapsed),
  fChild:  (p) => p instanceof Fill && ['or', 'either', 'whether'].includes(p.fill)
}
```

**Layout Semantics:**
- `All` (conjunction): Children arranged **horizontally** (sequential flow)
- `Any` (disjunction): Children arranged **vertically** (parallel paths)
- This visual metaphor mirrors circuit diagrams: series vs. parallel connections

**Example - British Nationality Act encoding:**

```typescript
com(
  all(
    com(say('the person is'),
        any(ele('born in UK after commencement'),
            say('or'),
            ele('born in qualifying territory'))),
    say('and'),
    com(say("the person's"),
        any(ele('father'), say('or'), ele('mother')),
        say('is'),
        any(ele('a British citizen'),
            say('or'),
            ele('settled in UK')))))
```

Expands to 2×2×3 = 12 DNF combinations when fully expanded, each representing a valid path to citizenship.

### React Components

- **`src/pages/index.tsx`** - Main app with document list sidebar and content pane
- **`src/pages/docview.tsx`** - Document viewer with:
  - `RenderOriginal` - Collapsed (single-line) view
  - `RenderSentences` - Expanded DNF combinations view
  - Reducer pattern for state management (`EXPAND`, `COLLAPSE`, `toggleParent`)
- **`src/pages/flow.tsx`** - ReactFlow wrapper handling node highlighting and click interactions
- **`src/pages/essay.tsx`** - Educational content about Boolean algebra in legal contexts

### Visualization

Uses ReactFlow for interactive diagrams. Custom node types:
- `connectorL` / `connectorR` - Invisible connection points at group boundaries
- `invisiHandles` - Fill nodes with transparent handles

AND groups arrange children horizontally; OR groups arrange children vertically. Nodes can be clicked to highlight satisfying paths through the diagram.

### Path Aliases

`@/*` maps to `./src/*` (configured in tsconfig.json)

## Example Documents

The app ships with several legal rule examples encoded in the DSL:
- British Nationality Act citizenship requirements
- Singapore Penal Code Section 415 (Cheating)
- Title insurance coverage clauses
- Abstract logic examples (ABCDE, Narnia crime rules)
