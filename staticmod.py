import json
from parser import Parser


class Base:
  def __init__(self, attrs, src=None):
    self.attrs = attrs
    self.src = src
    print(self.__class__)
    print(attrs)
    print()

class SystemAST(Base):
  pass

class SystemItem(Base):
  pass

class NamespaceDecl(Base):
  pass

class NamespaceItem(Base):
  pass

class StructDecl(Base):
  pass

class EnumDecl(Base):
  pass

class FuncDecl(Base):
  pass

class ProcedureDecl(Base):
  pass

class ModuleDecl(Base):
  pass

class ModuleItemSeq(Base):
  pass

class ModuleItem(Base):
  pass

class StateVarDecl(Base):
  pass

class ProcessDecl(Base):
  pass

class AssignDecl(Base):
  pass

class ModuleInst(Base):
  pass

class Statement(Base):
  pass

class AssertStmt(Base):
  pass

class AssignStmt(Base):
  pass

class AtomicStmt(Base):
  pass

class BlockStmt(Base):
  pass

class BreakStmt(Base):
  pass

class ContinueStmt(Base):
  pass

class EndStmt(Base):
  pass

class IfElseStmt(Base):
  pass

class MatchStmt(Base):
  pass

class ProcCallStmt(Base):
  pass

class ReturnStmt(Base):
  pass

class WaitStmt(Base):
  pass

class WhileStmt(Base):
  pass

class Expression(Base):
  pass

class MatchExpr(Base):
  pass

class IfElseExpr(Base):
  pass

class FuncCallExpr(Base):
  pass

class StructExpr(Base):
  pass

class EnumExpr(Base):
  pass

class BinaryOpExpr(Base):
  pass

class UnaryOpExpr(Base):
  pass

class LiteralExpr(Base):
  pass

class IdExpr(Base):
  pass

class NamespaceId(Base):
  pass

class ComposedId(Base):
  pass

class BaseId(Base):
  pass

class EnumItemDecl(Base):
  pass

class MatchArmStmt(Base):
  pass

class MatchOtherExpr(Base):
  pass

class MatchArmExpr(Base):
  pass

class EnumBinder(Base):
  pass


def dispatch(json_data):
  if isinstance(json_data, dict):
    if 'obj' in json_data:
      return deserialize(json_data)
    else:
      return {k: dispatch(v) for k, v in json_data.items()}
  elif isinstance(json_data, list):
    return [dispatch(item) for item in json_data]
  elif isinstance(json_data, (str, int)):
    return json_data


def deserialize(json_data):
  obj_name = json_data['obj']
  attrs_dict = json_data['attrs']
  src = json_data.get('src')
  deserialized_attrs = {k: dispatch(v) for k, v in attrs_dict.items()}
  return eval(obj_name)(deserialized_attrs, src)


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
  ast = deserialize(parser.json_ast)
