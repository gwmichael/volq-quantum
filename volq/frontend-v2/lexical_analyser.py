from .token import Token, TokenType

class Lexer:

    def __init__(self):
        self.code = None
        self.token_stream = []
        self.alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        self.numbers = "0123456789"
        self.punctuation = "(){}[].,"
        self.operators = "+-*/="
        self.string_punctuation = "\"\'"

    def load_program(self, code : str):
        self.code = code

    def tokenize_program(self):
        # scan characters at start of code until a space is reached
        # determine what type of token that the token is
        # append to token stream
        # remove token from code
        # repeat until EOF token is reached
        token_buffer = Token(None, None)
        while (token_buffer.type != TokenType.EOF):
            lexeme = self.scan_next_lexeme()
            token = self.classify_lexeme(lexeme)
            self.token_stream += token
            token_buffer = token

    def scan_next_lexeme(self):
        first_char = None
        # Get first character of lexeme
        try:
            while True:
                first_char = self.code[0]
                self.code = self.code[1:]
                # Check if it's a space, otherwise repeat
                if first_char != " ":
                    break
        except (IndexError):
            return ""
        # Determine how to continue
        match first_char:
            # Punctuation and operators
            case first_char if first_char in self.punctuation + self.operators:
                return first_char
            # Alphabet
            case first_char if first_char in self.alphabet:
                string_buffer = first_char
                while True:
                    next_char = self.code[0]
                    if (next_char in self.alphabet):
                        string_buffer += next_char
                        self.code = self.code[1:]
                    else:
                        return string_buffer
            # Numbers (without decimals, maybe TODO later)
            case first_char if first_char in self.numbers:
                string_buffer = first_char
                while True:
                    next_char = self.code[0]
                    if (next_char in self.numbers):
                        string_buffer += next_char
                        self.code = self.code[1:]
                    else:
                        return string_buffer
            # Reading strings
            #case first_char if first_char in self.string_punctuation:
                
    def classify_lexeme(self, lexeme: str):
        match lexeme:
            case "":
                return Token(TokenType.EOF)
            case lexeme if lexeme in self.operators:
                return Token(TokenType.OPERATOR, lexeme)
            case lexeme if lexeme in self.punctuation:
                return Token(TokenType.SEPARATOR, lexeme)
            case lexeme if lexeme[0] in self.string_punctuation and lexeme[len[lexeme]-1] in self.string_punctuation:
                return Token(TokenType.LITERAL, lexeme)
