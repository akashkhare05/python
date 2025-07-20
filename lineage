import os
import re
import argparse
from collections import defaultdict
import json

# Regex patterns
CREATE_TABLE_PATTERN = re.compile(r'create\s+(table|view)\s+(\w+)', re.IGNORECASE)
INSERT_INTO_PATTERN = re.compile(r'insert\s+into\s+(\w+)', re.IGNORECASE)
FROM_PATTERN = re.compile(r'from\s+([a-zA-Z0-9_,\s]+)', re.IGNORECASE)

def extract_dependencies(sql):
    dependencies = []
    target = None

    # Normalize newlines and spaces
    sql = re.sub(r'\s+', ' ', sql.strip())

    # Identify target table/view
    match_create = CREATE_TABLE_PATTERN.search(sql)
    match_insert = INSERT_INTO_PATTERN.search(sql)
    if match_create:
        target = match_create.group(2)
    elif match_insert:
        target = match_insert.group(1)

    # Identify source tables
    match_from = FROM_PATTERN.findall(sql)
    if match_from:
        for match in match_from:
            sources = [s.strip() for s in match.split(',') if s.strip()]
            dependencies.extend(sources)

    return target, dependencies

def scan_sql_files(root_path):
    lineage_map = defaultdict(set)

    for dirpath, _, filenames in os.walk(root_path):
        for file in filenames:
            if file.endswith('.sql'):
                full_path = os.path.join(dirpath, file)
                with open(full_path, 'r') as f:
                    content = f.read().lower()
                    statements = content.split(';')
                    for stmt in statements:
                        target, sources = extract_dependencies(stmt)
                        if target and sources:
                            lineage_map[target].update(sources)
    return lineage_map

def main():
    parser = argparse.ArgumentParser(description="Extract table lineage from SQL files")
    parser.add_argument('--path', required=True, help='Path to SQL code directory')
    args = parser.parse_args()

    lineage = scan_sql_files(args.path)

    # Output lineage map as JSON
    print(json.dumps({k: list(v) for k, v in lineage.items()}, indent=2))

if __name__ == '__main__':
    main()
