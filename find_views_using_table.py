import os
import re
import argparse

def find_views_using_table(view_path, target_table):
    matches = []
    pattern = re.compile(rf'\b(from|join)\s+{re.escape(target_table)}\b', re.IGNORECASE)

    for filename in os.listdir(view_path):
        if filename.endswith('.sql'):
            full_path = os.path.join(view_path, filename)
            with open(full_path, 'r') as f:
                content = f.read()

                if pattern.search(content):
                    matches.append(filename)

    return matches

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find views that depend on a given table.")
    parser.add_argument("--table", required=True, help="Target table name (e.g., orders)")
    parser.add_argument("--path", required=True, help="Path to views folder")

    args = parser.parse_args()
    found_views = find_views_using_table(args.path, args.table)

    if found_views:
        print(f"✅ Views using table '{args.table}':")
        for view in found_views:
            print(f" - {view}")
    else:
        print(f"❌ No views found using table '{args.table}'")
