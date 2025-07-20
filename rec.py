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

def normalize_name(name):
    """ Normalize SQL names: strip quotes, downcase, remove ~schema~ if present """
    name = name.strip().lower().replace('"', '')
    name = re.sub(r'~[^~]+~\.', '', name)  # remove ~schema~.
    return name

def parse_view_dependencies(files):
    """ Parse SQL files to build a map of view definitions and what each uses """
    view_definitions = {}         # view_name -> file_path
    view_dependencies = defaultdict(set)  # view_name -> set of objects it uses

    for filepath in files:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            content = re.sub(r'\s+', ' ', content)  # collapse whitespace

            # match "create view viewname as" or "insert into viewname"
            view_match = re.search(r'(create\s+view|insert\s+into)\s+([\w\."]+)', content)
            if view_match:
                raw_view_name = view_match.group(2)
                view_name = normalize_name(raw_view_name)
                view_definitions[view_name] = filepath

                # find FROM or JOIN usage
                matches = re.findall(r'(from|join)\s+([\w~\."]+)', content)
                for _, raw_dep in matches:
                    dep = normalize_name(raw_dep)
                    if dep != view_name:
                        view_dependencies[view_name].add(dep)

    return view_definitions, view_dependencies

def build_reverse_tree(start_object, view_dependencies):
    """ Build and print a reverse dependency tree (who uses what) """
    reverse_tree = defaultdict(set)
    for view, deps in view_dependencies.items():
        for dep in deps:
            reverse_tree[dep].add(view)

    visited = set()

    def print_tree(node, prefix=""):
        if node in visited:
            return
        visited.add(node)
        print(prefix + node)
        for child in sorted(reverse_tree.get(node, [])):
            print_tree(child, prefix + "    └── ")

    print_tree(start_object.lower())

def main(table_name, base_path):
    print(f"\n🔍 Searching for usage of: {table_name}\n")
    sql_files = find_sql_files(base_path)
    view_defs, view_deps = parse_view_dependencies(sql_files)

    table_name_norm = normalize_name(table_name)

    # quick check if table is used anywhere
    used_anywhere = any(table_name_norm in deps for deps in view_deps.values())
    if not used_anywhere:
        print("❌ No views or insert targets found using the table.")
        return

    print("✅ Dependency Tree:\n")
    build_reverse_tree(table_name_norm, view_deps)

# Example usage:
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python find_table_tree.py <table_name> <base_path>")
    else:
        table_name = sys.argv[1]
        base_path = sys.argv[2]
        main(table_name, base_path)
