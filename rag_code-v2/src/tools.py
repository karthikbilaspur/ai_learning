import ast, math, operator, time
from typing import Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class CalculatorInput(BaseModel):
    model_config=ConfigDict(extra="forbid")
    expression: str=Field(min_length=1,max_length=200)

_ALLOWED_BINOPS={ast.Add:operator.add,ast.Sub:operator.sub,ast.Mult:operator.mul,ast.Div:operator.truediv,ast.Mod:operator.mod,ast.Pow:operator.pow,ast.FloorDiv:operator.floordiv}
_ALLOWED_UNARYOPS={ast.UAdd:operator.pos,ast.USub:operator.neg}
_ALLOWED_FUNCS={n:getattr(math,n) for n in ("sqrt","sin","cos","tan","log","log10","exp","floor","ceil","fabs")}
_MAX_ABS=1e100; _MAX_EXP=1000
class UnsafeExpressionError(ValueError): pass

def _eval(node):
    if isinstance(node,ast.Expression): return _eval(node.body)
    if isinstance(node,ast.Constant) and isinstance(node.value,(int,float)) and math.isfinite(node.value): return node.value
    if isinstance(node,ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        a,b=_eval(node.left),_eval(node.right)
        if type(node.op) is ast.Pow and abs(b)>_MAX_EXP: raise UnsafeExpressionError("Exponent too large")
        out=_ALLOWED_BINOPS[type(node.op)](a,b)
        if isinstance(out,(int,float)) and (not math.isfinite(out) or abs(out)>_MAX_ABS): raise UnsafeExpressionError("Result outside safe numeric range")
        return out
    if isinstance(node,ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS: return _ALLOWED_UNARYOPS[type(node.op)](_eval(node.operand))
    if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in _ALLOWED_FUNCS and not node.keywords:
        return _ALLOWED_FUNCS[node.func.id](*[_eval(x) for x in node.args])
    raise UnsafeExpressionError(f"Unsupported expression element: {type(node).__name__}")

def safe_eval_math(expr:str):
    try: tree=ast.parse(expr.strip(),mode="eval")
    except SyntaxError as e: raise UnsafeExpressionError("Invalid expression") from e
    return _eval(tree)

class ToolRouter:
    def validate(self,name,args):
        if name!="calculator": raise ValueError(f"Unknown tool {name}")
        return CalculatorInput(**args)
    def execute(self,name,args)->Dict[str,Any]:
        self.validate(name,args); start=time.perf_counter()
        try: result=safe_eval_math(args["expression"]); return {"tool":name,"result":result,"latency_ms":round((time.perf_counter()-start)*1000,2)}
        except (UnsafeExpressionError,ZeroDivisionError,OverflowError,ValueError,TypeError) as e: return {"tool":name,"error":str(e),"latency_ms":round((time.perf_counter()-start)*1000,2)}
router=ToolRouter()
