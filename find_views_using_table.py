import os
import re

def find_views_using_table(view_path, target_table):
    target_table = target_table.lower()
    matches = []

    for filename in os.listdir(view_path):
        if filename.endswith('.sql'):
            full_path = os.path.join(view_path, filename)
            with open(full_path, 'r') as f:
                content = f.read().lower()

                # Check if the table appears in a FROM clause or JOIN clause
                if re.search(rf'\b(from|join)\s+{target_table}\b', content):
                    matches.append(filename)

    return matches

if __name__ == "__main__":
    # Hardcoded path to views folder and target table
    views_folder = "/home/youruser/sql-repo/views"
    table_to_search = "orders"  # 🔁 Change this to your input

    found_views = find_views_using_table(views_folder, table_to_search)

    if found_views:
        print(f"✅ Views that use table '{table_to_search}':")
        for view in found_views:
            print(f" - {view}")
    else:
        print(f"❌ No views found using table '{table_to_search}'")
