import os
import ast

def process_file(filepath):
    with open(filepath, 'r') as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        return

    insertions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            for item in node.body:
                if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                    func_name = item.name
                    args = [a.arg for a in item.args.args if a.arg not in ('self', 'cls')]
                    if item.args.vararg:
                        args.append('*' + item.args.vararg.arg)
                    if item.args.kwarg:
                        args.append('**' + item.args.kwarg.arg)
                    
                    args_str = ', '.join([f"{a}={{{a}}}" for a in args])
                    args_display = f" with {args_str}" if args else ""
                    
                    log_stmt = f'logger.info(f"Entered {func_name} of {class_name}{args_display}")'
                    
                    # find where to insert:
                    # after docstring if exists
                    body_start = item.body[0].lineno
                    if isinstance(item.body[0], ast.Expr) and isinstance(item.body[0].value, ast.Constant) and isinstance(item.body[0].value.value, str):
                        if len(item.body) > 1:
                            body_start = item.body[1].lineno
                        else:
                            body_start = item.body[0].end_lineno + 1
                            
                    insertions.append((body_start, log_stmt, item.col_offset + 4))
        
        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            # top-level functions
            if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) if hasattr(parent, 'body') and node in parent.body) : # not foolproof but close enough for simple ast.walk? parent is not in ast.walk.
                pass # let's manage parent manually

    # Better way: track parents
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            child.parent = node

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            
            # Check if it's a method
            parent = getattr(node, 'parent', None)
            is_method = isinstance(parent, ast.ClassDef)
            class_name = parent.name if is_method else ""
            
            args = [a.arg for a in node.args.args if a.arg not in ('self', 'cls')]
            if node.args.vararg:
                args.append('*' + node.args.vararg.arg)
            if node.args.kwarg:
                args.append('**' + node.args.kwarg.arg)
            
            args_str = ', '.join([f"{a}={{{a}}}" for a in args])
            args_display = f" with {args_str}" if args else ""
            
            if is_method:
                log_stmt = f'logger.info(f"Entered {func_name} of {class_name}{args_display}")'
            else:
                log_stmt = f'logger.info(f"Entered {func_name}{args_display}")'

            # avoid double inserting
            if any(isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call) and getattr(stmt.value.func, 'attr', '') == 'info' for stmt in node.body):
                continue # likely already has logging
            
            body_start = node.body[0].lineno
            insertions.append((body_start, log_stmt, node.col_offset + 4))

    insertions = sorted(list(set(insertions)), key=lambda x: x[0], reverse=True)
    
    if not insertions:
        return
        
    lines = source.split('\n')
    
    for line_num, log_stmt, indent in insertions:
        lines.insert(line_num - 1, " " * indent + log_stmt)
        
    has_logger = any("logger = Logger" in line for line in lines)
    if not has_logger:
        # find imports
        import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                import_idx = i + 1
        
        lines.insert(import_idx, "logger = Logger(__name__)")
        lines.insert(import_idx, "from app.core.logging import Logger")
        
    with open(filepath, 'w') as f:
        f.write('\n'.join(lines))
    print(f"Updated {filepath}")

for root, dirs, files in os.walk('app'):
    for file in files:
        if file.endswith('.py') and file != 'logging.py':
            process_file(os.path.join(root, file))

