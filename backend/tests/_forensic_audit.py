"""Comprehensive forensic analysis of the project."""
import ast
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BACKEND = os.path.join(ROOT, "backend", "app")
LEGACY = os.path.join(ROOT, "daragent-backend")
SCHEMAS_DIR = os.path.join(BACKEND, "schemas")
MODELS_DIR = os.path.join(BACKEND, "models")
SERVICES_DIR = os.path.join(BACKEND, "services")
REPOS_DIR = os.path.join(BACKEND, "repositories")
ROUTER_FILE = os.path.join(BACKEND, "api", "v1", "router.py")

def collect_py_files(root_dir):
    """Yield (filepath, relpath) for all .py files."""
    for dirpath, _, filenames in os.walk(root_dir):
        if '__pycache__' in dirpath:
            continue
        for fname in filenames:
            if fname.endswith('.py'):
                fpath = os.path.join(dirpath, fname)
                relpath = os.path.relpath(fpath, root_dir)
                yield fpath, relpath

def parse_file(filepath):
    """Parse a Python file, return AST or None on error."""
    try:
        with open(filepath, encoding='utf-8') as f:
            return ast.parse(f.read(), filename=filepath)
    except Exception as e:
        return None

def collect_definitions(root_dir):
    """Collect all class and function definitions with their locations."""
    classes = {}
    functions = {}
    for fpath, relpath in collect_py_files(root_dir):
        tree = parse_file(fpath)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes.setdefault(node.name, []).append((relpath, node.lineno, [b.id if isinstance(b, ast.Name) else str(b) for b in node.bases]))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.setdefault(node.name, []).append((relpath, node.lineno, 'async' if isinstance(node, ast.AsyncFunctionDef) else 'sync'))
    return classes, functions

# 1. Collect all definitions from backend/app
classes, functions = collect_definitions(BACKEND)

# Filter out __init__ which is expected in every class
classes_filtered = {k: v for k, v in classes.items() if k != '__init__'}
functions_filtered = {k: v for k, v in functions.items() if k != '__init__'}

print("=" * 70)
print("DUPLICATE CLASSES (same class name in multiple files)")
print("=" * 70)
dup_classes = {k: v for k, v in classes_filtered.items() if len(set(p[0] for p in v)) > 1}
for name, locs in sorted(dup_classes.items()):
    print(f"\n{name}:")
    for fpath, line, bases in locs:
        print(f"  class in {fpath}:{line} (bases: {bases})")

print("\n" + "=" * 70)
print("DUPLICATE FUNCTIONS (same function name in multiple files)")
print("=" * 70)
dup_funcs = {k: v for k, v in functions_filtered.items() if len(set(p[0] for p in v)) > 1}
for name, locs in sorted(dup_funcs.items()):
    print(f"\n{name}:")
    for fpath, line, kind in locs:
        print(f"  {kind}_func in {fpath}:{line}")

# 2. Check router registration
print("\n" + "=" * 70)
print("ROUTER REGISTRATION ANALYSIS")
print("=" * 70)
with open(ROUTER_FILE, encoding='utf-8') as f:
    router_content = f.read()

# Find all router includes
import_lines = re.findall(r'from\s+([\w.]+)\s+import\s+(\w+)', router_content)
included_modules = set()
included_vars = set()
for mod, var in import_lines:
    included_modules.add(mod)
    included_vars.add(var)

# Find all router definitions
router_defs = {}
for fpath, relpath in collect_py_files(os.path.join(BACKEND, "api", "v1")):
    tree = parse_file(fpath)
    if tree is None:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == 'router':
                    if isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Attribute):
                            pass
                        elif isinstance(node.value.func, ast.Name) and node.value.func.id == 'APIRouter':
                            prefix = None
                            for kw in node.value.keywords:
                                if kw.arg == 'prefix':
                                    if isinstance(kw.value, ast.Constant):
                                        prefix = kw.value.value
                                    elif isinstance(kw.value, ast.JoinedStr):
                                        prefix = '<f-string>'
                            router_defs[relpath] = prefix

# Check if each router module is included
included_path_patterns = set()
for mod, var in import_lines:
    # Convert module path to file path
    # e.g., app.api.v1.recommendations -> recommendations.py
    parts = mod.replace('app.api.v1.', '').replace('app.api.', '').split('.')
    if len(parts) >= 3:
        fpath = os.path.join(*parts) + '.py'
        included_path_patterns.add(fpath)

print("Router files and their registration status:")
for relpath, prefix in sorted(router_defs.items()):
    # Simpler check: see if the router variable name is mentioned
    varname = os.path.splitext(os.path.basename(relpath))[0] + '_router'
    included = varname in router_content or basename in router_content
    status = "REGISTERED" if included else "NOT REGISTERED"
    print(f"  {relpath} (prefix={prefix}): {status}")

# 3. Check models vs migrations
print("\n" + "=" * 70)
print("MODELS vs MIGRATIONS")
print("=" * 70)
migrations_dir = os.path.join(ROOT, "backend", "migrations", "versions")
model_files = {}
for fpath, relpath in collect_py_files(MODELS_DIR):
    tree = parse_file(fpath)
    if tree is None:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and base.id == 'Base':
                    model_files[node.name] = relpath

# Collect all migration column/table references
migration_tables = set()
for fpath, relpath in collect_py_files(migrations_dir):
    with open(fpath, encoding='utf-8') as f:
        content = f.read()
    # Find table definitions in migrations
    tables = re.findall(r'table=[\'"]?(\w+)', content)
    migration_tables.update(tables)

print("Models and their migration status:")
for model_name, relpath in sorted(model_files.items()):
    table_name = model_name.lower() + 's'  # plural convention
    # Check if table is mentioned in any migration
    found = False
    for fpath, _ in collect_py_files(migrations_dir):
        with open(fpath, encoding='utf-8') as f:
            content = f.read()
        if model_name in content or model_name.lower() in content.lower():
            found = True
            break
    status = "FOUND IN MIGRATION" if found else "NOT IN MIGRATION"
    print(f"  {model_name} ({relpath}): {status}")

# 4. Check for __import__ usage
print("\n" + "=" * 70)
print("__import__ USAGE CHECK")
print("=" * 70)
import_builtins = []
for fpath, relpath in collect_py_files(BACKEND):
    with open(fpath, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if '__import__' in line:
                import_builtins.append(f"  {relpath}:{i}: {line.strip()}")
if import_builtins:
    for item in import_builtins:
        print(item)
else:
    print("  No __import__ usage found")

# 5. Check for self.db.add without await flush
print("\n" + "=" * 70)
print("REPOSITORIES USING self.db.add (async context)")
print("=" * 70)
repo_add_patterns = []
for fpath, relpath in collect_py_files(REPOS_DIR):
    with open(fpath, encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if 'self.db.add' in line and 'await' not in line:
                repo_add_patterns.append(f"  {relpath}:{i}: {line.strip()}")
if repo_add_patterns:
    for item in repo_add_patterns:
        print(item)
else:
    print("  No unawaited self.db.add found")

# 6. Check old/legacy directories
print("\n" + "=" * 70)
print("LEGACY DIRECTORIES")
print("=" * 70)
if os.path.isdir(LEGACY):
    files = list(collect_py_files(LEGACY))
    print(f"  daragent-backend/ directory: {len(files)} Python files")
    print(f"  Contains api/{len([f for f in files if 'api' in f[1]])} API files, "
          f"models/, core/, ai_providers/")
    print("  STATUS: LEGACY - DO NOT USE")
else:
    print("  No legacy directory found")

# 7. Check for services that import db directly without dependency injection
print("\n" + "=" * 70)
print("API ENDPOINTS USING Repository Directly (bypassing service layer)")
print("=" * 70)
for fpath, relpath in collect_py_files(os.path.join(BACKEND, "api", "v1")):
    tree = parse_file(fpath)
    if tree is None:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and 'repositories' in node.module:
                for alias in node.names:
                    print(f"  {relpath}: imports {alias.name} from {node.module}")

# 8. Schema usage analysis
print("\n" + "=" * 70)
print("UNUSED SCHEMA CLASSES")
print("=" * 70)
schema_classes = {}
for fpath, relpath in collect_py_files(SCHEMAS_DIR):
    tree = parse_file(fpath)
    if tree is None:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            schema_classes[node.name] = (relpath, node.lineno)

# Check which schemas are imported anywhere in the backend, excluding the schemas dir itself
imported_schemas = set()
for fpath, relpath in collect_py_files(BACKEND):
    if 'schemas/' in relpath:
        continue
    tree = parse_file(fpath)
    if tree is None:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and 'schemas' in node.module:
                for alias in node.names:
                    imported_schemas.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if 'schemas' in alias.name:
                    imported_schemas.add(alias.name.split('.')[-1])

# Also check web-app types
web_types_dir = os.path.join(ROOT, "web-app", "src", "types")
web_imported_schemas = set()
if os.path.isdir(web_types_dir):
    for fpath, relpath in collect_py_files(web_types_dir):
        with open(fpath, encoding='utf-8') as f:
            content = f.read()
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'types' in (node.module or ''):
                    for alias in node.names:
                        web_imported_schemas.add(alias.name)

all_imported_schemas = imported_schemas | web_imported_schemas
for name, (relpath, line) in sorted(schema_classes.items()):
    if name not in all_imported_schemas:
        print(f"  {name} in {relpath}:{line}")

# 9. Service usage analysis
print("\n" + "=" * 70)
print("SERVICES NEVER IMPORTED")
print("=" * 70)
service_classes = {}
for fpath, relpath in collect_py_files(SERVICES_DIR):
    tree = parse_file(fpath)
    if tree is None:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            service_classes[node.name] = (relpath, node.lineno)

# Check which services are imported
imported_services = set()
for fpath, relpath in collect_py_files(BACKEND):
    if relpath.startswith('services/'):
        continue
    tree = parse_file(fpath)
    if tree is None:
        continue
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and 'services' in node.module:
                for alias in node.names:
                    imported_services.add(alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if 'services' in alias.name:
                    imported_services.add(alias.name.split('.')[-1])

for name, (relpath, line) in sorted(service_classes.items()):
    if name not in imported_services:
        # Check if it's used in the same file (e.g., AIOrchestrator uses internal)
        with open(os.path.join(SERVICES_DIR, relpath), encoding='utf-8') as f:
            content = f.read()
        if f'{name}(' in content or f'{name}.' in content:
            # Check if it's used outside its own file
            pass
        else:
            print(f"  {name} in {relpath}:{line}")

# Check imports from services directory
for fpath, relpath in collect_py_files(BACKEND):
    if 'services/' not in relpath:
        tree = parse_file(fpath)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and 'services.ai' in node.module:
                    for alias in node.names:
                        print(f"  {relpath} imports {alias.name} from {node.module}")
