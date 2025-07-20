import os
import re
from collections import defaultdict

def find_sql_files(base_path):
    """Recursively find all .sql files under base_path."""
    sql_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(".sql"):
                sql_files.append(os.path.join(root, file))
    return sql_files

def parse_definitions_and_dependencies(files):
    """Parse all .sql files and return view definitions and their dependencies."""
    definitions = {}  # object_name (usually view) -> file_path
    dependencies = defaultdict(set)  # object_name -> set of table/view it uses

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()

            # Match CREATE VIEW or INSERT INTO object_name
            def_match = re.search(r'(create\s+view|insert\s+into)\s+([\w\."]+)', content)
            if def_match:
                object_name = def_match.group(2).strip('"')
                definitions[object_name] = filepath

                # Find all FROM and JOIN targets
                matches = re.findall(r'(from|join)\s+([\w\."]+)', content)
                for _, target in matches:
                    target = target.strip('"')
                    if target != object_name:
                        dependencies[object_name].add(target)
    return definitions, dependencies

def build_reverse_dependency_tree(target, dependencies):
    """Print reverse dependency tree from target."""
    reverse_tree = defaultdict(set)

    for obj, deps in dependencies.items():
        for dep in deps:
            reverse_tree[dep].add(obj)

    def build_tree(node, level=0, visited=set()):
        indent = "    " * level + ("↳ " if level > 0 else "")
        print(f"{indent}{node}")
        if node in visited:
            return
        visited.add(node)
        for child in sorted(reverse_tree.get(node, [])):
            build_tree(child, level + 1, visited)

    build_tree(target.lower())

def normalize_name(name):
    """Lowercase and remove double quotes."""
    return name.lower().replace('"', '')

def main(table_name, base_path):
    table_name = normalize_name(table_name)
    print(f"\n🔍 Finding views that depend on: {table_name}\n")

    sql_files = find_sql_files(base_path)
    defs, deps = parse_definitions_and_dependencies(sql_files)

    all_objects = set(defs.keys()).union(*deps.values())

    # Check if the exact name is present
    matches = [obj for obj in all_objects if obj.endswith(table_name)]
    if not matches:
        print(f"❌ No object found using or matching '{table_name}'")
        return

    # Start tree from all matching base names (with or without schema)
    print("✅ Dependency Tree:\n")
    for match in matches:
        build_reverse_dependency_tree(match, deps)

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python find_view_dependencies.py <table_name> <base_path>")
    else:
        table_name = sys.argv[1]
        base_path = sys.argv[2]
        main(table_name, base_path)
