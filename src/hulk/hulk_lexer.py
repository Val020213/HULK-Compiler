from hulk.utils import Token
from hulk.lexer.regex import Regex
from cmp.automata import State
from hulk.hulk_grammar import G as hulk_grammar
from hulk.lexer.regex_grammar import G
from hulk.parser.lr1 import LR1Parser
from serialized.Serialized import Serialized


class Lexer:
    def __init__(self, table, eof, load=False, save=False):
        self.errors = []
        self.eof = eof
        self.parser = LR1Parser(G)
        print("regex parser build")

        serilizer = Serialized()

        if load:
            print("LOADING REGEX 😱...")
            try:
                self.regexs = serilizer.load_object("regexs")
                print("REGEX LOADED OK! 🥵✅")
            except:
                print("Load regex failed...")
                save = True
                load = False
        if save:
            self.regexs = self._build_regexs(table)
            serilizer.save_object(object=self.regexs, object_name="regexs")

        self.automaton = self._build_automaton()

    def _build_regexs(self, table):
        regexs = []
        for n, (token_type, regex, is_regex) in enumerate(table):
            states = State.from_nfa(Regex(regex, is_regex, self.parser).automaton)
            for v in states:
                if v.final:
                    v.tag = (n, token_type)
            regexs.append(states)
        return regexs

    def _build_automaton(self):
        start = State("start")
        for regex in self.regexs:
            start.add_epsilon_transition(regex)
        return start.to_deterministic()

    def _walk(self, string):
        state = self.automaton
        final = state if state.final else None
        final_lex = lex = ""
        for symbol in string:
            new_state = state[symbol]
            if new_state is not None and new_state[0] is not None:
                new_state = new_state[0]
                lex += symbol

                if new_state.final:

                    if new_state.tag is None:
                        new_state.tag = list(
                            map(
                                lambda x: x.tag,
                                filter(lambda x: x.tag is not None, new_state.state),
                            )
                        )

                    final = new_state
                    final_lex = lex
                state = new_state
            else:
                break

        return final, final_lex

    def _tokenize(self, text):

        row = 1
        column = 1

        while text:

            if text[0] == " ":
                column += 1
                text = text[1:]
                continue

            if text[0] == "\n":
                row += 1
                column = 1
                text = text[1:]
                continue

            final, final_lex = self._walk(text)

            if len(final_lex) == 0:
                self.errors.append(f"Invalid token at line: {row}, column: {column}")
                text = text[1:]
                continue

            try:
                n, token_type = min(final.tag)
            except:
                print("============", final, "============")
                print(final_lex)
                print(f"row: {row}, column: {column}")
                print(final.tag)

            text = text[len(final_lex) :]

            yield final_lex, token_type, row, column

            column += len(final_lex)

        yield "$", self.eof, row, column

    def __call__(self, text):
        return [
            Token(lex, hulk_grammar[str(token_type)], row, column)
            for lex, token_type, row, column in self._tokenize(text)
        ]
