#!/usr/bin/env python3
"""
Poh Yuan Nie v PP [2022] SGCA 74 — surplusage as boolean minimisation.

Watch the 'dishonest concealment' literal VANISH from the minimised formula under
the applicants' reading, while surviving as essential under the court's. That
disappearance IS the presumption against surplusage, computed: a clause the
minimiser can delete is a clause that does no work.

The real Espresso (via pyeda) wouldn't install here — Homebrew's Python 3.14 has a
broken expat, so pip itself crashes, and there's no espresso binary. So this rolls
the minimiser by hand: Quine–McCluskey, the EXACT two-level minimisation algorithm
that Espresso approximates heuristically for speed. On a problem this small, QM
returns the provably-minimal cover — i.e. precisely what Espresso aims at.

    python3 cheating-415-espresso.py        # no dependencies
"""

# ---------------------------------------------------------------------------
# A tiny exact two-level minimiser (Quine–McCluskey + essential-PI / greedy cover)
# ---------------------------------------------------------------------------
def _combine(a, b, n):
    diff = -1
    for i in range(n):
        if (a[i] is None) != (b[i] is None):
            return None
        if a[i] != b[i]:
            if diff != -1:
                return None
            diff = i
    if diff == -1:
        return None
    r = list(a); r[diff] = None
    return tuple(r)

def _prime_implicants(minterms, n):
    cur = {tuple((m >> (n - 1 - i)) & 1 for i in range(n)) for m in minterms}
    primes = set()
    while cur:
        used, nxt = set(), set()
        terms = list(cur)
        for i in range(len(terms)):
            for j in range(i + 1, len(terms)):
                c = _combine(terms[i], terms[j], n)
                if c is not None:
                    used.add(terms[i]); used.add(terms[j]); nxt.add(c)
        primes |= {t for t in terms if t not in used}
        cur = nxt
    return primes

def _covered(impl, n):
    free = [i for i in range(n) if impl[i] is None]
    base = sum(1 << (n - 1 - i) for i in range(n) if impl[i] == 1)
    out = set()
    for k in range(1 << len(free)):
        m = base
        for b, i in enumerate(free):
            if (k >> b) & 1:
                m |= 1 << (n - 1 - i)
        out.add(m)
    return out

def minimise(varnames, onset):
    """onset: set of minterm ints. Returns a minimal list of implicants (tuples of 0/1/None)."""
    n = len(varnames)
    if not onset:
        return []                              # constant FALSE
    if len(onset) == (1 << n):
        return [tuple([None] * n)]             # constant TRUE
    primes = list(_prime_implicants(onset, n))
    pcov = {p: _covered(p, n) & onset for p in primes}
    chosen, covered = set(), set()
    # essential prime implicants
    changed = True
    while changed:
        changed = False
        for m in onset - covered:
            covering = [p for p in primes if m in pcov[p]]
            if len(covering) == 1 and covering[0] not in chosen:
                chosen.add(covering[0]); covered |= pcov[covering[0]]; changed = True
    # greedy cover for the remainder
    while covered < onset:
        best = max(primes, key=lambda p: len(pcov[p] - covered))
        chosen.add(best); covered |= pcov[best]
    return list(chosen)

def term_str(impl, varnames):
    parts = [("" if v == 1 else "¬") + varnames[i] for i, v in enumerate(impl) if v is not None]
    return " ∧ ".join(parts) if parts else "TRUE"

def sop_str(cover, varnames):
    if not cover:
        return "FALSE"
    return "   ∨   ".join(term_str(t, varnames) for t in cover)

def support(cover, varnames):
    return {varnames[i] for impl in cover for i, v in enumerate(impl) if v is not None}

def build_onset(func, reading, free_vars, fixed):
    n = len(free_vars)
    on = set()
    for x in range(1 << n):
        v = dict(fixed)
        for i, name in enumerate(free_vars):
            v[name] = bool((x >> (n - 1 - i)) & 1)
        if func(reading, v):
            on.add(x)
    return on

# ---------------------------------------------------------------------------
# s 415 (2008), the same model as the L4 file and the Z3 proof
# ---------------------------------------------------------------------------
def concealment_counts(reading, v):
    return (v['conceal'] and v['prop_intent']) if reading == 'Second' else v['conceal']

def deception(reading, v):
    return v['by_deceiving'] or concealment_counts(reading, v)

def first_limb(reading, v):
    return deception(reading, v) and (v['fraudulently'] or v['prop_intent']) and v['prop_delivery']

def second_limb(reading, v):
    return (deception(reading, v) and v['intentionally'] and v['causes_harm']
            and (v['harm_body'] or v['harm_mind'] or v['harm_reputation'] or v['harm_property']))

def cheats(reading, v):
    return first_limb(reading, v) or second_limb(reading, v)

NICE = {'by_deceiving': 'by-deceiving', 'conceal': 'DISHONEST-CONCEALMENT',
        'intentionally': 'intentionally', 'causes_harm': 'causes-harm',
        'harm_body': 'harm-body', 'harm_mind': 'harm-mind',
        'harm_reputation': 'harm-reputation', 'harm_property': 'harm-property'}

# ===========================================================================
print("=" * 78)
print("DEMO 1 — the deception gateway, minimised in the no-property world")
print("=" * 78)
print("Explanation 1 only matters through 'there is a deception'. Minimise that,")
print("with no property (s 24 gate off), under each reading:\n")
gw_vars = ['by_deceiving', 'conceal']
labels  = [NICE[v] for v in gw_vars]
for reading, who in [('Fourth', "the court's reading"), ('Second', "the applicants' reading")]:
    on = build_onset(deception, reading, gw_vars, {'prop_intent': False})
    cover = minimise(gw_vars, on)
    gone = "" if 'conceal' in support(cover, gw_vars) else "   <-- DISHONEST-CONCEALMENT ELIMINATED"
    print(f"  {who:24}  deception  =  {sop_str(cover, labels)}{gone}")

print()
print("=" * 78)
print("DEMO 2 — the whole offence, minimised in the no-property world")
print("=" * 78)
print("Minimise 'is said to cheat' over the 8 non-property atoms, under each")
print("reading. Count how many product terms still mention DISHONEST-CONCEALMENT:\n")
free = ['by_deceiving', 'conceal', 'intentionally', 'causes_harm',
        'harm_body', 'harm_mind', 'harm_reputation', 'harm_property']
labels = [NICE[v] for v in free]
fixed = {'prop_intent': False, 'prop_delivery': False, 'fraudulently': False}
for reading, who in [('Fourth', "the court's reading"), ('Second', "the applicants' reading")]:
    on = build_onset(cheats, reading, free, fixed)
    cover = minimise(free, on)
    n_terms = len(cover)
    n_conceal = sum(1 for t in cover if t[free.index('conceal')] is not None)
    insupport = 'conceal' in support(cover, free)
    print(f"  {who}:")
    print(f"      minimal cover has {n_terms} product terms; "
          f"{n_conceal} mention DISHONEST-CONCEALMENT  "
          f"(in support: {insupport})")
    print(f"      {sop_str(cover, labels)}\n")

print("=" * 78)
print("The minimiser deletes the clause the court called 'otiose'. Surplusage")
print("and dead-code elimination are the same operation. (GD [30], [32].)")
print("=" * 78)
