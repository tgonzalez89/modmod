from ply.yacc import yacc
from lexer import Lexer
import json


'''
TODO:
  * send/receive/has message
  * resets for processes and reg state vars
  * dependencies statements and dependencies for state vars (fatal when reading/writing and dep is not met)
  * arrays of state vars, modules and inside structs
  * check for empty seqs here or later?
'''


class Parser(Lexer):

  # ----------------------------------------------------------------------------
  #      System & Items
  # ----------------------------------------------------------------------------

  def p_SystemAST(self, p):
    #"SystemAST : Expression"
    #p[0] = p[1]
    "SystemAST : SystemItemSeq"
    p[0] = {
      'obj': 'SystemAST',
      'attrs': {
        'items': p[1],
      },
    }
    self.json_ast = p[0]
    self.json_ast_str = json.dumps(p[0], indent=self.json_indent)

  def p_SystemItemSeq(self, p):
    '''SystemItemSeq : empty
                     | SystemItem
                     | SystemItem SystemItemSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[2]

  def p_SystemItem(self, p):
    '''SystemItem : NamespaceDecl
                  | ModuleDecl'''
    p[0] = p[1]

  # ----------------------------------------------------------------------------
  #      Namespace & Items
  # ----------------------------------------------------------------------------

  def p_NamespaceDecl(self, p):
    "NamespaceDecl : namespace Identifier '{' NamespaceItemSeq '}'"
    p[0] = {
      'obj': 'NamespaceDecl',
      'attrs': {
        'name': p[2],
        'items': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_NamespaceItemSeq(self, p):
    '''NamespaceItemSeq : empty
                        | NamespaceItem
                        | NamespaceItem NamespaceItemSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[2]

  def p_NamespaceItem(self, p):
    '''NamespaceItem : StructDecl
                     | EnumDecl
                     | FuncDecl
                     | ProcedureDecl
                     | ModuleDecl'''
    p[0] = p[1]

  def p_StructDecl(self, p):
    "StructDecl : struct Identifier '{' StructFieldDeclSeq '}'"
    p[0] = {
      'obj': 'StructDecl',
      'attrs': {
        'name': p[2],
        'fields': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_EnumDecl(self, p):
    "EnumDecl : enum Identifier '{' EnumItemDeclSeq '}'"
    p[0] = {
      'obj': 'EnumDecl',
      'attrs': {
        'name': p[2],
        'items': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_FuncDecl(self, p):
    "FuncDecl : func TypeId Identifier '(' ArgDeclSeq ')' '=' Expression ';'"
    p[0] = {
      'obj': 'FuncDecl',
      'attrs': {
        'type': p[2],
        'name': p[3],
        'args': p[5],
        'body': p[8],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_ProcedureDecl(self, p):
    "ProcedureDecl : procedure Identifier '(' ArgDeclSeq ')' Statement"
    p[0] = {
      'obj': 'ProcedureDecl',
      'attrs': {
        'name': p[2],
        'args': p[4],
        'body': p[6],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  # ----------------------------------------------------------------------------
  #      Module & Items
  # ----------------------------------------------------------------------------

  def p_ModuleDecl(self, p):
    "ModuleDecl : module Identifier '{' ModuleItemSeq '}'"
    p[0] = {
      'obj': 'ModuleDecl',
      'attrs': {
        'name': p[2],
        'items': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_ModuleItemSeq(self, p):
    '''ModuleItemSeq : empty
                     | ModuleItem
                     | ModuleItem ModuleItemSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[2]

  def p_ModuleItem(self, p):
    '''ModuleItem : StateVarDecl
                  | ProcessDecl
                  | AssignDecl
                  | ModuleInst'''
    p[0] = p[1]

  def p_StateVarDecl(self, p):
    """StateVarDecl : StateVarKind TypeId Identifier ';'
                    | StateVarKind TypeId Identifier '=' Expression ';'"""
    p[0] = {
      'obj': 'StateVarDecl',
      'attrs': {
        'kind': p[1].value,
        'type': p[2],
        'name': p[3],
      },
      'src': {
        'line': p[1].lineno,
        'col': self.find_column(p[1]),
      },
    }
    if len(p) > 5:
      p[0]['attrs']['initial'] = p[5]

  def p_ProcessDecl(self, p):
    "ProcessDecl : process Identifier Statement"
    p[0] = {
      'obj': 'ProcessDecl',
      'attrs': {
        'name': p[2],
        'body': p[3],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_AssignDecl(self, p):
    "AssignDecl : assign AssignStmt"
    p[0] = {
      'obj': 'AssignDecl',
      'attrs': p[2]['attrs'],
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_ModuleInst(self, p):
    "ModuleInst : NamespaceId Identifier '(' AssignmentSeq ')' ';'"
    p[0] = {
      'obj': 'ModuleInst',
      'attrs': {
        'class': p[1],
        'name': p[2],
        'params': p[4],
      },
      'src': p[1]['src'],
    }

  # ----------------------------------------------------------------------------
  #      Statements
  # ----------------------------------------------------------------------------

  def p_Statement(self, p):
    '''Statement : AssertStmt
                 | AssignStmt
                 | AtomicStmt
                 | BlockStmt
                 | BreakStmt
                 | ContinueStmt
                 | EndStmt
                 | IfElseStmt
                 | MatchStmt
                 | ProcCallStmt
                 | ReturnStmt
                 | WaitStmt
                 | WhileStmt'''
    p[0] = p[1]

  def p_AssertStmt(self, p):
    "AssertStmt : assert Expression ';'"
    p[0] = {
      'obj': 'AssertStmt',
      'attrs': {
        'expr': p[2],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_AssignStmt(self, p):
    "AssignStmt : Assignment ';'"
    p[0] = {
      'obj': 'AssignStmt',
      'attrs': p[1],
      'src': p[1]['lhs']['src'],
    }

  def p_AtomicStmt(self, p):
    "AtomicStmt : atomic Statement"
    p[0] = {
      'obj': 'AtomicStmt',
      'attrs': {
        'stmt': p[2],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_BlockStmt(self, p):
    "BlockStmt : '{' StmtSeq '}'"
    p[0] = {
      'obj': 'BlockStmt',
      'attrs': {
        'stmts': p[2],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_BreakStmt(self, p):
    "BreakStmt : break ';'"
    p[0] = {
      'obj': 'BreakStmt',
      'attrs': {},
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_ContinueStmt(self, p):
    "ContinueStmt : continue ';'"
    p[0] = {
      'obj': 'ContinueStmt',
      'attrs': {},
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_EndStmt(self, p):
    "EndStmt : end ';'"
    p[0] = {
      'obj': 'EndStmt',
      'attrs': {},
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_IfElseStmt(self, p):
    '''IfElseStmt : if Expression Statement else Statement
                  | if Expression Statement'''
    p[0] = {
      'obj': 'IfElseStmt',
      'attrs': {
        'cond': p[2],
        'true_arm': p[3],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }
    if len(p) > 4:
      p[0]['attrs']['false_arm'] = p[5]

  def p_MatchStmt(self, p):
    "MatchStmt : match Expression '{' MatchArmStmtSeq MatchOtherStmt '}'"
    p[0] = {
      'obj': 'MatchStmt',
      'attrs': {
        'subject': p[2],
        'arms': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }
    if p[5] is not None:
      p[0]['attrs']['other'] = p[5]

  def p_ProcCallStmt(self, p):
    """ProcCallStmt : NamespaceId '(' ExprSeq ')'
                    | IdExpr '(' ExprSeq ')'"""
    p[0] = {
      'obj': 'ProcCallExpr',
      'attrs': {
        'name': p[1] if p[1]['obj'] == 'NamespaceId' else p[1]['attrs']['id'],
        'args': p[3],
      },
      'src': p[1]['src'],
    }

  def p_ReturnStmt(self, p):
    "ReturnStmt : return ';'"
    p[0] = {
      'obj': 'ReturnStmt',
      'attrs': {},
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_WaitStmt(self, p):
    "WaitStmt : wait Expression ';'"
    p[0] = {
      'obj': 'WaitStmt',
      'attrs': {
        'expr': p[2],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_WhileStmt(self, p):
    "WhileStmt : while Expression Statement"
    p[0] =  {
      'obj': 'WhileStmt',
      'attrs': {
        'cond': p[2],
        'body': p[3],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  # ----------------------------------------------------------------------------
  #      Expressions
  # ----------------------------------------------------------------------------

  def p_Expression(self, p):
    '''Expression : IdExpr
                  | LiteralExpr
                  | UnaryOpExpr
                  | BinaryOpExpr
                  | EnumExpr
                  | StructExpr
                  | FuncCallExpr
                  | IfElseExpr
                  | MatchExpr'''
    p[0] = p[1]

  def p_MatchExpr(self, p):
    "MatchExpr : match Expression '{' MatchArmExprSeq MatchOtherExpr '}'"
    p[0] = {
      'obj': 'MatchExpr',
      'attrs': {
        'subject': p[2],
        'arms': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }
    if p[5] is not None:
      p[0]['attrs']['other'] = p[5]

  def p_IfElseExpr(self, p):
    "IfElseExpr : if Expression Expression else Expression"
    p[0] = {
      'obj': 'IfElseExpr',
      'attrs': {
        'cond': p[2],
        'true_arm': p[3],
        'false_arm': p[5],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_FuncCallExpr(self, p):
    """FuncCallExpr : NamespaceId '(' ExprSeq ')'
                    | IdExpr '(' ExprSeq ')'"""
    p[0] = {
      'obj': 'FuncCallExpr',
      'attrs': {
        'name': p[1] if p[1]['obj'] == 'NamespaceId' else p[1]['attrs']['id'],
        'args': p[3],
      },
      'src': p[1]['src'],
    }

  def p_StructExpr(self, p):
    """StructExpr : NamespaceId '{' AssignmentSeq '}'
                  | IdExpr '{' AssignmentSeq '}'"""
    p[0] = {
      'obj': 'StructExpr',
      'attrs': {
        'type': p[1] if p[1]['obj'] == 'NamespaceId' else p[1]['attrs']['id'],
        'vals': p[3],
      },
      'src': p[1]['src'],
    }

  def p_EnumExpr(self, p):
    '''EnumExpr : NamespaceId
                | NamespaceId '#' Expression'''
    if p[1]['obj'] != 'NamespaceId':
      raise NameError(f"Invalid enum tag: '{p[1]['attrs']['name']}'")
    p[0] = {
      'obj': 'EnumExpr',
      'attrs': {
        'tag': p[1],
      },
      'src': p[1]['src'],
    }
    if len(p) > 2:
      p[0]['attrs']['val'] = p[3]

  def p_BinaryOpExpr(self, p):
    p[0] = {
      'obj': 'BinaryOpExpr',
      'attrs': {
        'lhs': p[1],
        'op': self.binary_operators[p[2]][0],
        'rhs': p[3],
      },
      'src': p[1]['src'],
    }

  def p_UnaryOpExpr(self, p):
    # Transform to negative int literal
    if (self.unary_operators[p[1]][0] == 'UnaryMinusOp' and
        p[2]['obj'] == 'LiteralExpr' and
        p[2]['attrs']['type'] == 'int'):
      p[2]['attrs']['val'] = p[1] + p[2]['attrs']['val']
      p[0] = p[2]
    # Keep as unary op expr
    else:
      p[0] = {
      'obj': 'UnaryOpExpr',
      'attrs': {
        'op': self.unary_operators[p[1]][0],
        'expr': p[2],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_ParenExpr(self, p):
    "Expression : '(' Expression ')'"
    p[0] = p[2]

  def p_IntLiteralExpr(self, p):
    '''LiteralExpr : IntLiteral'''
    p[0] = {
      'obj': 'LiteralExpr',
      'attrs': {
        'val': p[1],
        'type': 'int',
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_BoolLiteralExpr(self, p):
    '''LiteralExpr : true
                   | false'''
    p[0] = {
      'obj': 'LiteralExpr',
      'attrs': {
        'val': p[1],
        'type': 'bool',
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_IdExpr(self, p):
    '''IdExpr : BaseId
              | ComposedId'''
    p[0] = {
      'obj': 'IdExpr',
      'attrs': {
        'id': p[1],
      },
      'src': p[1]['src'],
    }

  # ----------------------------------------------------------------------------
  #      Identifiers
  # ----------------------------------------------------------------------------

  def p_TypeId(self, p):
    '''TypeId : NamespaceId
              | int
              | bool'''
    if type(p[1]) == dict:
      p[0] = p[1]
    else:
      p[0] = {
        'obj': 'BaseId',
        'attrs': {
          'name': p[1],
        },
        'src': {
          'line': p.slice[1].lineno,
          'col': self.find_column(p.slice[1]),
        },
      }

  def p_NamespaceId(self, p):
    '''NamespaceId : BaseId
                   | NamespaceId ColonColon Identifier'''
    if (len(p) == 2):
      p[0] = p[1]
    else:
      p[0] = {
        'obj': 'NamespaceId',
        'attrs': {
          'name': p[3],
          'rest': p[1],
        },
        'src': {
          'line': p.slice[3].lineno,
          'col': self.find_column(p.slice[3]),
        },
      }

  def p_ComposedId(self, p):
    '''ComposedId : BaseId
                  | ComposedId '.' Identifier'''
    if (len(p) == 2):
      p[0] = p[1]
    else:
      p[0] = {
        'obj': 'ComposedId',
        'attrs': {
          'name': p[3],
          'rest': p[1],
        },
        'src': {
          'line': p.slice[3].lineno,
          'col': self.find_column(p.slice[3]),
        },
      }

  def p_BaseId(self, p):
    "BaseId : Identifier"
    p[0] = {
      'obj': 'BaseId',
      'attrs': {
        'name': p[1],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  # ----------------------------------------------------------------------------
  #      Helper and Misc. Grammar Rules
  # ----------------------------------------------------------------------------

  def p_StructFieldDeclSeq(self, p):
    '''StructFieldDeclSeq : empty
                          | StructFieldDecl
                          | StructFieldDecl ',' StructFieldDeclSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[3]

  def p_StructFieldDecl(self, p):
    "StructFieldDecl : TypeId Identifier"
    p[0] = {
      'type': p[1],
      'name': p[2],
    }

  def p_EnumItemDeclSeq(self, p):
    '''EnumItemDeclSeq : empty
                       | EnumItemDecl
                       | EnumItemDecl ',' EnumItemDeclSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[3]

  def p_EnumItemDecl(self, p):
    '''EnumItemDecl : TypeId Identifier
                    | Identifier'''
    if len(p) > 2:
      p[0] = {
        'type': p[1],
        'name': p[2],
      }
    else:
      p[0] = {
        'name': p[1],
      }

  def p_ArgDeclSeq(self, p):
    '''ArgDeclSeq : empty
                  | ArgDecl
                  | ArgDecl ',' ArgDeclSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[3]

  def p_ArgDecl(self, p):
    "ArgDecl : TypeId Identifier"
    p[0] = {
      'type': p[1],
      'name': p[3],
    }

  def p_StateVarKind(self, p):
    '''StateVarKind : inwire
                    | outwire
                    | outreg
                    | reg
                    | wire
                    | const'''
    p[0] = p.slice[1]

  def p_StmtSeq(self, p):
    '''StmtSeq : empty
               | Statement
               | Statement StmtSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[2]

  def p_MatchOtherStmt(self, p):
    '''MatchOtherStmt : empty
                      | other ':' Statement'''
    if p[1] is None:
      p[0] = p[1]
    else:
      p[0] = p[3]

  def p_MatchArmStmtSeq(self, p):
    '''MatchArmStmtSeq : empty
                       | MatchArmStmt
                       | MatchArmStmt MatchArmStmtSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[2]

  def p_MatchArmStmt(self, p):
    '''MatchArmStmt : case EnumBinder ':' Statement
                    | case Expression ':' Statement'''
    p[0] = {
      'obj': 'MatchArmStmt',
      'attrs': {
        'pattern': p[2],
        'body': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_MatchOtherExpr(self, p):
    '''MatchOtherExpr : empty
                      | other ':' Expression'''
    if p[1] is None:
      p[0] = p[1]
    else:
      p[0] = p[3]

  def p_MatchArmExprSeq(self, p):
    '''MatchArmExprSeq : empty
                       | MatchArmExpr
                       | MatchArmExpr MatchArmExprSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[2]

  def p_MatchArmExpr(self, p):
    '''MatchArmExpr : case EnumBinder ':' Expression
                    | case Expression ':' Expression'''
    p[0] = {
      'obj': 'MatchArmExpr',
      'attrs': {
        'pattern': p[2],
        'body': p[4],
      },
      'src': {
        'line': p.slice[1].lineno,
        'col': self.find_column(p.slice[1]),
      },
    }

  def p_EnumBinder(self, p):
    '''EnumBinder : NamespaceId '@' Identifier'''
    if p[1]['obj'] != 'NamespaceId':
      raise NameError(f"Invalid enum tag: '{p[1]['attrs']['name']}'")
    p[0] = {
      'obj': 'EnumBinder',
      'attrs': {
        'tag': p[1],
        'binder': p[3],
      },
      'src': p[1]['src'],
    }

  def p_ExprSeq(self, p):
    '''ExprSeq : empty
               | Expression
               | Expression ',' ExprSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[3]

  def p_AssignmentSeq(self, p):
    '''AssignmentSeq : empty
                     | Assignment
                     | Assignment ',' AssignmentSeq'''
    p[0] = []
    if p[1] is not None:
      p[0].append(p[1])
    if len(p) > 2:
      p[0] += p[3]

  def p_Assignment(self, p):
    "Assignment : ComposedId '=' Expression"
    p[0] = {
      'lhs': p[1],
      'rhs': p[3],
    }

  def p_empty(self, p):
    'empty :'
    pass

  def p_error(self, p):
    if p:
      raise SyntaxError(f"Syntax error at '{p.value}', line {p.lineno}, column {self.find_column(p)}")
    else:
      raise SyntaxError(f"Syntax error at EOF")

  # ----------------------------------------------------------------------------
  #      Class Methods
  # ----------------------------------------------------------------------------

  def __init__(self, data=None, json_indent=None):
    super().__init__(data)

    self.json_indent = json_indent
    self.json_ast = {}
    self.json_ast_str = ""

    # Remove backslashes from token definitions
    for d in (self.unary_operators, self.binary_operators):
      for k in tuple(d.keys()):
        d[k.replace('\\', '')] = d.pop(k)

    # Create the precedence list
    ops = list(self.unary_operators.values()) + list(self.binary_operators.values())
    max_precedence = max(ops, key = lambda v: v[2])[2] + 1
    self.precedence = [None] * max_precedence
    for v in ops:
      if type(v[2]) != int or v[2] >= len(self.precedence):
        raise IndexError(f"Ill defined operator precedence in '{v}'")
      if self.precedence[v[2]] is None:
        self.precedence[v[2]] = [v[1], v[0]]
      elif v[1] != self.precedence[v[2]][0]:
        raise LookupError(f"Ill defined operator precedence in '{v}'")
      else:
        self.precedence[v[2]].append(v[0])

    # Create the doc strings for the operator expression functions
    lines = (f"{v[0]} Expression\n| " for v in list(self.unary_operators.values())[:-1])
    joined = "".join(lines)
    self.__class__.p_UnaryOpExpr.__doc__ = f"UnaryOpExpr : {joined}{'SubOp Expression %prec UnaryMinusOp'}"

    lines = (f"Expression {v[0]} Expression" for v in self.binary_operators.values())
    joined = "\n| ".join(lines)
    self.__class__.p_BinaryOpExpr.__doc__ = f"BinaryOpExpr : {joined}"

  def build(self, **kwargs):
    super().build(**kwargs)
    self.parser = yacc(module=self, **kwargs)
    return self.parser

  def parse(self, data=None):
    if data is not None:
      self.data = data
    self.parser.parse(self.data)

  def find_column(self, token):
    line_start = self.data.rfind('\n', 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


if __name__ == '__main__':
  from sys import argv
  from pathlib import Path
  if len(argv) < 2:
    exit()
  infilepath = argv[1]
  data = ""
  with open(infilepath, 'r') as file:
    data = file.read()
  parser = Parser(data, 2)
  parser.build()
  parser.parse()
  outfilename = Path(infilepath).stem
  with open(outfilename + '.json', 'w') as file:
    file.write(parser.json_ast)
