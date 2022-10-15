from ply.lex import lex


class Lexer:
  keywords = {
    # Upper level keywords
    'include', 'namespace', 'module', 'struct', 'enum', 'func', 'procedure',
    # Module level keywords
    'process', 'assign',
    # State variable keywords
    'inwire', 'outwire', 'outreg', 'wire', 'reg', 'const',
    # Statement and expression keywords
    'if', 'else', 'while', 'match', 'case', 'other',
    'wait', 'assert', 'atomic',
    'break', 'continue', 'return', 'end',
    # Built-in types
    'int', 'bool',
    # Literals
    'true', 'false',
  }

  unary_operators = {
    r'~': ('BitwiseNotOp', 'right', 9),
    r'!': ('LogicNotOp',   'right', 9),
    r'-': ('UnaryMinusOp', 'right', 9),
  }

  binary_operators = {
    r'\*':   ('MulOp',           'left',     8),
    r'/':    ('DivOp',           'left',     8),
    r'%':    ('RemOp',           'left',     8),
    r'\+':   ('AddOp',           'left',     7),
    r'-':    ('SubOp',           'left',     7),
    r'<<':   ('LeftShiftOp',     'left',     6),
    r'>>':   ('RightShiftOp',    'left',     6),
    r'&':    ('BitwiseAndOp',    'left',     5),
    r'\^':   ('XorOp',           'left',     4),
    r'\|':   ('BitwiseOrOp',     'left',     3),
    r'==':   ('EqualsOp',        'nonassoc', 2),
    r'!=':   ('NotEqualsOp',     'nonassoc', 2),
    r'<':    ('LessThanOp',      'nonassoc', 2),
    r'<=':   ('LessThanEqOp',    'nonassoc', 2),
    r'>':    ('GreaterThanOp',   'nonassoc', 2),
    r'>=':   ('GreaterThanEqOp', 'nonassoc', 2),
    r'&&':   ('LogicAndOp',      'left',     1),
    r'\|\|': ('LogicOrOp',       'left',     0),
  }

  operators = {**unary_operators, **binary_operators}

  tokens = tuple(keywords) + \
    tuple(v[0] for v in operators.values()) + \
    ('ColonColon', 'IntLiteral', 'Identifier')

  literals = (
    '=',
    '(', ')',
    '{', '}',
    '#' ,'@',
    '.', ',', ';', ':',
  )

  t_ColonColon = r'::'

  t_IntLiteral = r'(0b[01]+)|(0o[0-7]+)|(0x[0-9a-fA-F])|(\d+)'

  def t_Identifier(self, t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value in self.keywords:
      t.type = t.value
    return t

  def t_comment_single_line(self, t):
    r'//.*?(\n|$)'
    t.lexer.lineno += t.value.count('\n')

  def t_comment_multiline(self, t):
    r'/\*(.|\n)*?\*/'
    t.lexer.lineno += t.value.count('\n')

  def t_newline(self, t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')

  t_ignore = " \t"

  def t_error(self, t):
    raise SyntaxError(f"Illegal character '{t}'")

  def __init__(self, data=None):
    self.data = data if data is not None else ""

    # Create the tokens for the operators
    for k, v in self.operators.items():
      setattr(self, f"t_{v[0]}", k)

  def build(self, **kwargs):
    self.lexer = lex(module=self, **kwargs)
    return self.lexer

  def tokenize(self, data=None):
    if data is not None:
      self.data = data
    self.lexer.input(self.data)
    return self.lexer


if __name__ == '__main__':
  from sys import argv
  if len(argv) < 2:
    exit()
  lexer = Lexer(argv[1])
  lexer.build()
  tokens = lexer.tokenize()
  for tok in tokens:
    print(tok)
