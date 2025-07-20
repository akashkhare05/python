import os
import re
from collections import defaultdict

def find_sql_files(base_path):
    """ Recursively find all .sql files under base_path """
    sql_files = []
    for root, _, files in os.walk(base_path):
        for file in files:
            if file.lower().endswith(".sql"):
                sql_files.append(os.path.join(root, file))
    return sql_files

def parse_view_dependencies(files):
    """ Parse views and build a map of view definitions and their dependencies """
    view_definitions = {}         # view_name -> file_path
    view_dependencies = defaultdict(set)  # view_name -> set of object names (tables or views) it uses

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            # find view name
            view_match = re.search(r'create\s+view\s+([\w\."]+)', content)
            if view_match:
                view_name = view_match.group(1).strip('"')
                view_definitions[view_name] = filepath

                # find dependencies in FROM / JOIN clauses (simplified)
                matches = re.findall(r'(from|join)\s+([\w\."]+)', content)
                for _, obj in matches:
                    dep = obj.strip('"')
                    if dep != view_name:
                        view_dependencies[view_name].add(dep)
    return view_definitions, view_dependencies

def build_reverse_dependency_tree(target, view_dependencies):
    """ Build reverse tree: for each view, who uses it """
    reverse_tree = defaultdict(set)
    for view, deps in view_dependencies.items():
        for dep in deps:
            reverse_tree[dep].add(view)

    # recursive tree builder
    def build_tree(node, level=0, visited=set()):
        indent = "    " * level + ("↳ " if level > 0 else "")
        print(f"{indent}{node}")
        if node in visited:
            return
        visited.add(node)
        for child in sorted(reverse_tree.get(node, [])):
            build_tree(child, level + 1, visited)

    build_tree(target.lower())

def main(table_name, base_path):
    print(f"\n🔍 Searching for usage of: {table_name}\n")
    sql_files = find_sql_files(base_path)
    view_defs, view_deps = parse_view_dependencies(sql_files)

    table_name = table_name.lower()
    used_directly = [view for view, deps in view_deps.items() if table_name in deps]

    if not used_directly:
        print("❌ No views found using the table or view.")
        return

    print("✅ Dependency Tree:\n")
    build_reverse_dependency_tree(table_name, view_deps)

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python find_view_dependencies.py <table_name> <base_path>")
    else:
        table_name = sys.argv[1]
        base_path = sys.argv[2]
        main(table_name, base_path)
