# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is Meng's sandbox within the SMUCCLAW project - a collection of experimental prototypes exploring legal technology concepts. The projects relate to L4, a domain-specific language for formalizing legal rules (contracts, regulations, legislation) as executable specifications with formal verification capabilities.

## Technology Stack

### Haskell Projects (most projects)
Built with Stack. Standard commands:
```bash
cd <project>
stack build
stack run <executable-name>
stack test
```

Projects: `alleninterval`, `burrito`, `dungeons-and-dragons/edsl`, `hxtfun`, `models20201113`, `mymodels`, `optparsesimple`, `pnml`, `readsheets`, `sprmrkt`, `ttt`

### PureScript Projects
Built with Spago:
```bash
spago build
spago bundle-app --to ./dist/app.js
```

Projects: `halogen-parent-child`, `purescript`

### TypeScript/JavaScript Projects
Built with Next.js:
```bash
npm install
npm run dev    # development server
npm run build  # production build
npm run lint   # run eslint with --fix
```

Projects: `layman`, `pdfdiff-halogen`

### Prolog
Run with SWI-Prolog: `swipl <file>.pl`

## Key Project Purposes

- **alleninterval**: Derives Allen's interval algebra from timepoint algebra; demonstrates temporal logic reasoning
- **natural-asp**: Explores syntax for Natural L4 that compiles to Answer Set Programming
- **pnml**: Experiments with Petri nets, process algebras, and workflow modeling for contract representation
- **dungeons-and-dragons/edsl**: Embedded DSL for state machines and Petri nets with GraphViz visualization
- **layman**: React/Next.js app for interactive visualization of and/or trees (legal decision logic)
- **halogen-parent-child**: PureScript Halogen experiments with component composition and dependency logic

## Domain Concepts

When working in this codebase, be aware of these L4/legal-tech concepts:
- **Constitutive rules** (statics): and/or trees, Boolean structures
- **Regulative rules** (dynamics): state machines, Petri nets, temporal workflows
- **Deontic logic**: obligations, permissions, prohibitions (MAY, MUST, SHANT)
- **Temporal logic**: deadlines, durations, Allen interval relations
- **Defeasibility**: rules that can be overridden by other rules
