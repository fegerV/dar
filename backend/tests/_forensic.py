"""Forensic project structure analysis."""
import ast, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app")

# 1. Collect all classes, functions, imports
definitions = {}  # name -> [(file, line, kind)]
imports = {}    # module -> set of imported names
routers = []
schemas_files = {}

for root, dirs, fnames in os.walk(APP):
    for f in fnames:
        if not f.endswith(".py"):
            continue
        path = os.path.join(root, f)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        try:
            tree = ast.parse(content, filename=path)
        except SyntaxError as e:
            print(f"SYNTAX_ERROR: {path}: {e}")
            continue
        rel = os.path.relpath(path, APP)
        imports[rel] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                definitions.setdefault(node.name, []).append((rel, node.lineno, "class"))
                if any(isinstance(b, ast.Name) and b.id == "APIRouter" for b in node.bases):
                    routers.append((rel, node.name, node.lineno))
            elif isinstance(node, ast.FunctionDef):
                definitions.setdefault(node.name, []).append((rel, node.lineno, "func"))
            elif isinstance(node, ast.AsyncFunctionDef):
                definitions.setdefault(node.name, []).append((rel, node.lineno, "async_func"))
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports[rel].add(alias.name)

# 2. Check which schemas are imported
schema_dir = os.path.join(APP, "schemas")
if os.path.isdir(schema_dir):
    for root, dirs, fnames in os.walk(schema_dir):
        for f in fnames:
            if f.endswith(".py") and not f.startswith("_"):
                sfile = os.path.join(root, f)
                with open(sfile, encoding="utf-8") as fh:
                    stree = ast.parse(fh.read())
                for node in ast.walk(stree):
                    if isinstance(node, ast.ClassDef):
                        schemas_files.setdefault(node.name, []).append(sfile)

# 3. Check router registration
with open(os.path.join(APP, "api", "v1", "router.py"), encoding="utf-8") as f:
    router_content = f.read()

print("=" * 70)
print("DUPLICATE CLASSES (same name in multiple files)")
print("=" * 70)
for name, locs in sorted(definitions.items()):
    if len(locs) > 1:
        files = set(l[0] for l in locs)
        if len(files) > 1:
            print(f"\n{name}:")
            for fpath, line, kind in locs:
                print(f"  {kind} in {fpath}:{line}")

print("\n" + "=" * 70)
print("ROUTERS NOT IN router.py")
print("=" * 70)
import re as _re
router_imports = _re.findall(r'from\s+\S+\s+import\s+\w*_router', router_content)
registered_routers = set()
for line in router_imports:
    parts = _re.findall(r'(\w+_router)', line)
    for p in parts:
        registered_routers.add(p)

for root, dirs, fnames in os.walk(os.path.join(APP, "api", "v1")):
    for f in fnames:
        if f.endswith(".py") and f != "__init__.py" and f != "router.py":
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            if "APIRouter(" in content:
                m = re.search(r'router = APIRouter\(([^)]*)\)', content)
                tag = m.group(1) if m else "?"
                base = f.replace(".py", "")
                router_var = f"{base}_router"
                registered = router_var in router_content
                status = "REGISTERED" if registered else "NOT REGISTERED"
                print(f"  {f}: {status}")

print("\n" + "=" * 70)
print("SCHEMAS NEVER IMPORTED")
print("=" * 70)
for sname, slocs in sorted(schemas_files.items()):
    imported = False
    for fpath, imp_set in imports.items():
        if sname in imp_set:
            imported = True
            break
    if not imported:
        for sloc in slocs:
            print(f"  {sname} in {sloc}")

# 4. Check services not imported
service_dir = os.path.join(APP, "services")
service_classes = {}
for root, dirs, fnames in os.walk(service_dir):
    for f in fnames:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            with open(path, encoding="utf-8") as fh:
                stree = ast.parse(fh.read())
            for node in ast.walk(stree):
                if isinstance(node, ast.ClassDef) and "Service" in node.name:
                    service_classes.setdefault(node.name, []).append(path)

print("\n" + "=" * 70)
print("SERVICES NEVER IMPORTED")
print("=" * 70)
for sname, locs in sorted(service_classes.items()):
    imported = False
    for fpath, imp_set in imports.items():
        if sname in imp_set and imp_set:
            imported = True
            break
    if not imported and len(locs) == 1:
        print(f"  {sname} in {locs[0]}")
