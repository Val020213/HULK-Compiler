from serialized.Serialized import Serialized


class ShiftReduceParser:
    SHIFT = "SHIFT"
    REDUCE = "REDUCE"
    OK = "OK"

    def __init__(self, G, verbose=False, load=False, save=False):
        self.G = G
        self.verbose = verbose
        self.action = {}
        self.goto = {}

        serialized_instance = Serialized()
        if load:
            self.action = serialized_instance.load_object("action")
            self.goto = serialized_instance.load_object("goto")

        else:
            self._build_parsing_table()

            if save:
                serialized_instance.save_object(self.action, "action")
                serialized_instance.save_object(self.goto, "goto")

    def _build_parsing_table(self):
        raise NotImplementedError()

    def notify_unexpected_symbols(self, current_token, expected_symbol):
        raise ValueError(
            "Unexpected symbol",
            current_token,
            # "in ",
            # current_token.row,
            # current_token.col,
            "Expected",
            expected_symbol,
        )

    # def find_unexpected_symbol_and_notify(self, state):
    #     state_expected, token_expected = filter(
    #         self.action.keys(), lambda x: x[0] == state
    #     )[0]
    #     self.notify_unexpected_symbols(state_expected, token_expected)

    def __call__(self, tokens):
        stack = [0]
        cursor = 0
        output = []
        operations = []
        w = [t.token_type for t in tokens]
        print(" = = = == = = = == = = = Tokens:  = = === = = = == = = = == = =", tokens)
        print(" = = = == = = = == = = = W:  = = === = = = == = = = == = =", w)
        while True:
            state = stack[-1]
            lookahead = w[cursor]
            if self.verbose:
                print(stack, "<---||--->", w[cursor:])

            # Your code here!!! (Detect error)
            if (state, lookahead) not in self.action.keys():
                # self.find_unexpected_symbol_and_notify(state)
                self.notify_unexpected_symbols(
                    lookahead,
                    f"EOF or some symbol that not appear, Current State {state}, lookahead {tokens[cursor].lex}",
                )
                return

            action, tag = self.action[state, lookahead]

            # Your code here!!! (Shift case)
            if action == ShiftReduceParser.SHIFT:
                stack.append(tag)
                cursor += 1
                operations.append(ShiftReduceParser.SHIFT)

            # Your code here!!! (Reduce case)
            elif action == ShiftReduceParser.REDUCE:
                production = tag
                for expected_symbol in production.Right:
                    symbol = stack.pop()
                    if symbol != expected_symbol:
                        print(
                            "Unexpected symbol popped from stack",
                            symbol,
                            "Expected",
                            expected_symbol,
                        )
                        self.notify_unexpected_symbols(w[cursor], expected_symbol)
                state = stack[-1]

                stack.append(production.Left)
                stack.append(self.goto[state, production.Left])

                output.append(production)
                operations.append(ShiftReduceParser.REDUCE)

            # Your code here!!! (OK case)
            elif action == ShiftReduceParser.OK:
                operations.append(ShiftReduceParser.OK)
                return output, operations

            # Your code here!!! (Invalid case)
            else:
                raise ValueError("Unknown action", action)
