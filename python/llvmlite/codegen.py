from lexParse import PrototypeAST, FunctionAST, Parser
from ctypes import CFUNCTYPE, c_double

import llvmlite.ir as ir
import llvmlite.binding as llvm


class CodegenError(Exception):
    pass


class LLVMCodeGenerator(object):
    def __init__(self):
        """
        Initialize the code generator.

        This creates a new LLVM module into which code is generated. The
        generateCode() method can be called multiple times. It adds the code
        generated for this node into the module, and returns the IR value for
        the node.

        At any time, the current LLVM module being constructed can be obtained
        from the module attribute.
        """
        self.module = ir.Module()

        # Current IR builder.
        self.builder = None

        # Manages a symbol table while a function is being codegen'd. Maps var
        # names to ir.Value
        self.functionSymbolTable = {}

    def generateCode(self, node):
        assert isinstance(node, (PrototypeAST, FunctionAST))
        return self._codegen(node)

    def _codegen(self, node):
        """
        Node visitor. Dispatches upon node type.
        For AST node of class Foo, calls self._codegen_Foo. Each visitor is
        expected to return a llvmlite.ir.Value.
        """
        method = '_codegen' + node.__class__.__name__
        return getattr(self, method)(node)

    def _codegenDoubleExprAST(self, node):
        return ir.Constant(ir.DoubleType(), float(node.val))

    def _codegenVariableExprAST(self, node):
        return self.functionSymbolTable[node.name]

    def _codegenBinaryExprAST(self, node):
        lhs = self._codegen(node.lhs)
        rhs = self._codegen(node.rhs)

        if node.op == '+':
            return self.builder.fadd(lhs, rhs, 'addtmp')
        elif node.op == '-':
            return self.builder.fsub(lhs, rhs, 'subtmp')
        elif node.op == '*':
            return self.builder.fmul(lhs, rhs, 'multmp')
        elif node.op == '<':
            lessThan = self.builder.fcmp_unordered('<', lhs, rhs, 'lttmp')
            # uitofp = unsigned integer to floating point
            return self.builder.uitofp(lessThan, ir.DoubleType(), 'booltmp')
        else:
            raise CodegenError('Unknown binary operator', node.op)

    def _codegenCallExprAST(self, node):
        calleeFunc = self.module.globals.get(node.callee, None)
        if calleeFunc is None or not isinstance(calleeFunc, ir.Function):
            raise CodegenError('Call to unknown function', node.callee)
        if len(calleeFunc.args) != len(node.args):
            raise CodegenError('Call argument length mismatch', node.callee)
        callArgs = [self._codegen(arg) for arg in node.args]
        return self.builder.call(calleeFunc, callArgs, 'calltmp')

    def _codegenPrototypeAST(self, node):
        funcName = node.name
        # Create a function type
        funcType = ir.FunctionType(ir.DoubleType(),
                                   [ir.DoubleType()] * len(node.argNames))

        # If a function with this name already exists in the module...
        if funcName in self.module.globals:
            # We do not allow redeclaration yet. Potentially worth changing later...
            raise CodegenError('Function/Global name collision', funcName)
        else:
            func = ir.Function(self.module, funcType, funcName)
        # Set function argument names from AST
        for i, arg in enumerate(func.args):
            arg.name = node.argNames[i]
            self.functionSymbolTable[arg.name] = arg
        return func

    def _codegenFunctionAST(self, node):
        # Reset the symbol table. Prototype generation will pre-populate it with
        # function arguments.
        self.functionSymbolTable = {}

        # Create the function skeleton from the prototype.
        func = self._codegen(node.proto)

        # Create the entry BB in the function and set the builder to it.
        basicBlockEntry = func.append_basic_block('entry')
        self.builder = ir.IRBuilder(basicBlockEntry)
        returnValue = self._codegen(node.body)
        self.builder.ret(returnValue)
        return func


class NicheEvaluator(object):
    """
    Evaluator for Niche expressions.

    Once an object is created, calls to evaluate() add new expressions to the
    module. Definitions (including imports) are only added into the IR - no
    JIT compilation occurs. When a toplevel expression is evaluated, the whole
    module is JITed and the result of the expression is returned.
    """
    def __init__(self):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.codegen = LLVMCodeGenerator()

        self.target = llvm.Target.from_default_triple()

    def evaluate(self, codeString, optimize=True, llvmdump=False):
        """
        Evaluate code in codestr.

        Returns 0.0 for definitions and import, and the evaluated expression
        value for toplevel expressions.
        """
        # Parse the given code and generate code from it
        ast = Parser().parseTopLevel(codeString)
        self.codegen.generateCode(ast)
        test = type(ast)

        if llvmdump:
            print('======== Unoptimized LLVM IR')
            print(str(self.codegen.module))

        # If we're evaluating a definition or import declaration, don't do
        # anything else. If we're evaluating an anonymous wrapper for a toplevel
        # expression, JIT-compile the module and run the function to get its
        # result.
        llvmmod = llvm.parse_assembly(str(self.codegen.module))

        #Optimize the module
        if optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 2
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvmmod)

            if llvmdump:
                print('======== Optimized LLVM IR')
                print(str(llvmmod))

        # Create a MCJIT execution engine to JIT-compile the module. Note that
        # ee takes ownership of target_machine, so it has to be recreated anew
        # each time we call create_mcjit_compiler.
        targetMachine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvmmod, targetMachine) as mcjitCompiler:
            mcjitCompiler.finalize_object()

            if llvmdump:
                print('======== Machine code')
                print(targetMachine.emit_assembly(llvmmod))

            result = 0.0
            if type(ast) == FunctionAST:
                functionPointer = CFUNCTYPE(c_double)(mcjitCompiler.get_function_address(ast.proto.name))
                result = functionPointer()
            return result
