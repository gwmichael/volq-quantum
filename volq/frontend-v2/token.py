import enum

class TokenType(enum.Enum):
    KEYWORD = "KEYWORD"
    IDENTIFIER = "IDENTIFIER"
    LITERAL = "LITERAL"
    OPERATOR = "OPERATOR"
    SEPARATOR = "SEPARATOR"
    COMMENT = "COMMENT"
    EOF = "EOF"

class Token:

    def __init__(self, type: TokenType, value: any = None):
        self.type = type
        self.value = value
