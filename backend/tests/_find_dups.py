import ast, os

classes = {}
for root, dirs, fnames in os.walk('app'):
    for f in fnames:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            try:
                with open(path, encoding='utf-8') as fh:
                    tree = ast.parse(fh.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        classes.setdefault(node.name, []).append((path, node.lineno))
            except:
                pass

for name, locs in sorted(classes.items()):
    if len(locs) > 1:
        print(f'=== {name} ===')
        for path, line in locs:
            print(f'  {path}:{line}')
