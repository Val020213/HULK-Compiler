# HULK — Compiler & Interpreter

An implementation of **HULK** (*Havana University Language for Kompilers*) — a strongly-typed, object-oriented, incremental teaching language — written from scratch in Python. No parser generator, no lexing library: the lexer generator, the LR(1) parser generator, the type system, and the evaluator are all built here.

Compilers course, Facultad de Matemática y Computación, University of Havana, 2024.
Language specification: <https://matcom.github.io/hulk/>

![HULK IDE](main.png)

---

## What's implemented

The full pipeline, source text → value:

**1. Lexer generator.** Token classes are declared as **regular expressions**, not hand-written matchers. The regexes are themselves parsed into an AST (`lexer/regex_ast.py`), compiled to an NFA via Thompson construction, then determinised and minimised into a DFA (`lexer/regex_automaton.py`). Tokenising is a walk over that DFA with maximal-munch, and every token carries its row and column for error reporting.

**2. LR(1) parser generator.** A canonical **LR(1)** table is computed from the grammar in `hulk/hulk_grammar.py` — closure over LR(1) items, GOTO, and the ACTION/GOTO tables (`parser/lr1.py`, `parser/shift_reduce.py`). Conflicts are reported against the grammar rather than silently resolved. Parsing produces a reverse derivation that is then evaluated into a typed AST.

**3. Semantic analysis** — a four-pass pipeline (`semantic_check/`):

| Pass | Responsibility |
| --- | --- |
| `type_collector` | Registers every `type` and `protocol` declaration |
| `type_builder` | Builds attributes, methods, inheritance chains, protocol conformance |
| `variable_collector` | Resolves scopes and bindings for `let`, `for`, function params |
| `type_checker` | Infers and checks expression types, `is` / `as`, method dispatch |

Errors accumulate rather than aborting on the first one, so a single run reports every problem in the file.

**4. Tree-walking interpreter** (`tree_interpeter/interpeter.py`) — evaluates the checked AST with dynamic dispatch, `self` / `base()` resolution, closures over `let`-bindings, and the built-in library (`print`, `range`, `sin`, `cos`, `sqrt`, `log`, `rand`, `PI`).

**Table caching.** Building the LR(1) tables and the lexer DFA is the expensive part, so both are serialized with `dill` into `cache_hulk/*.plk` and reloaded on subsequent runs (`load` / `save` flags in `src/main.py`).

### Language features covered

Functions (inline `=>` and block bodies) · `let … in` · `if / elif / else` as an expression · `while` and `for` · `type` declarations with constructors, attributes, methods and **inheritance** · `protocol` declarations with `extends` · runtime type tests `is` and downcasts `as` · vectors and **list comprehensions** (`[x^2 || x in range(1,10)]`) · string concatenation `@` and `@@` · destructive assignment `:=` · full arithmetic and boolean operators.

See [`test.hulk`](./test.hulk) for a program exercising all of it.

---

## Running it

```bash
pip install -r requirements.txt
```

**Web IDE** — editor, one-click run, and the diagnostics panel:

```bash
cd src
python -m streamlit run ./ide.py
```

**CLI** — runs the sample program in `src/main.py` and dumps every stage (tokens → parse → AST → semantic errors → evaluation):

```bash
cd src
python main.py
```

Set `load = False` in `main.py` / `ide.py` to rebuild the parser and lexer tables from scratch instead of loading the cached ones.

---

## Repository layout

```
src/
├─ hulk/
│  ├─ lexer/            # regex parser → NFA → DFA → tokenizer (lexer generator)
│  ├─ parser/           # canonical LR(1) table construction + shift-reduce driver
│  ├─ semantic_check/   # collector → builder → variable collector → type checker
│  ├─ tree_interpreter/  # AST evaluator
│  ├─ hulk_grammar.py   # the HULK grammar
│  └─ hulk_ast.py       # AST node definitions
├─ cmp/                 # shared compiler toolkit: grammars, automata, visitors
├─ ide.py               # Streamlit IDE
└─ main.py              # CLI entry point
cache_hulk/             # serialized parser tables and lexer DFA (.plk)
```

---

## Authors

- **Osvaldo Moreno** — [@Val020213](https://github.com/Val020213)
- **Daniel Toledo** — [@Phann020126](https://github.com/Phann020126)
- **Daniel Machado Pérez** — [@DanielMPMatCom](https://github.com/DanielMPMatCom)
