from .constants import CYPHER_DEFAULT_LIMIT

CYPHER_DELETE_ALL = "MATCH (n) DETACH DELETE n;"

CYPHER_LIST_PROJECTS = "MATCH (p:Project) RETURN p.name AS name ORDER BY p.name"

CYPHER_DELETE_PROJECT = """
MATCH (p:Project {name: $project_name})
OPTIONAL MATCH (p)-[:CONTAINS_PACKAGE|CONTAINS_FOLDER|CONTAINS_FILE|CONTAINS_MODULE*]->(container)
OPTIONAL MATCH (container)-[:DEFINES|DEFINES_METHOD*]->(defined)
DETACH DELETE p, container, defined
"""

CYPHER_EXAMPLE_DECORATED_FUNCTIONS = f"""MATCH (n:Function|Method)
WHERE ANY(d IN n.decorators WHERE toLower(d) IN ['flow', 'task'])
RETURN n.name AS name, n.qualified_name AS qualified_name, labels(n) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXAMPLE_CONTENT_BY_PATH = f"""MATCH (n)
WHERE n.path IS NOT NULL AND n.path STARTS WITH 'workflows'
RETURN n.name AS name, n.path AS path, labels(n) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXAMPLE_KEYWORD_SEARCH = f"""MATCH (n)
WHERE toLower(n.name) CONTAINS 'database' OR (n.qualified_name IS NOT NULL AND toLower(n.qualified_name) CONTAINS 'database')
RETURN n.name AS name, n.qualified_name AS qualified_name, labels(n) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXAMPLE_FIND_FILE = """MATCH (f:File) WHERE toLower(f.name) = 'readme.md' AND f.path = 'README.md'
RETURN f.path as path, f.name as name, labels(f) as type"""

CYPHER_EXAMPLE_README = f"""MATCH (f:File)
WHERE toLower(f.name) CONTAINS 'readme'
RETURN f.path AS path, f.name AS name, labels(f) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXAMPLE_PYTHON_FILES = f"""MATCH (f:File)
WHERE f.extension = '.py'
RETURN f.path AS path, f.name AS name, labels(f) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXAMPLE_TASKS = f"""MATCH (n:Function|Method)
WHERE 'task' IN n.decorators
RETURN n.qualified_name AS qualified_name, n.name AS name, labels(n) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXAMPLE_FILES_IN_FOLDER = f"""MATCH (f:File)
WHERE f.path STARTS WITH 'services'
RETURN f.path AS path, f.name AS name, labels(f) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXAMPLE_LIMIT_ONE = """MATCH (f:File) RETURN f.path as path, f.name as name, labels(f) as type LIMIT 1"""

CYPHER_EXAMPLE_CLASS_METHODS = f"""MATCH (c:Class)-[:DEFINES_METHOD]->(m:Method)
WHERE c.qualified_name ENDS WITH '.UserService'
RETURN m.name AS name, m.qualified_name AS qualified_name, labels(m) AS type
LIMIT {CYPHER_DEFAULT_LIMIT}"""

CYPHER_EXPORT_NODES = """
MATCH (n)
RETURN id(n) as node_id, labels(n) as labels, properties(n) as properties
"""

CYPHER_EXPORT_RELATIONSHIPS = """
MATCH (a)-[r]->(b)
RETURN id(a) as from_id, id(b) as to_id, type(r) as type, properties(r) as properties
"""

CYPHER_RETURN_COUNT = "RETURN count(r) as created"
CYPHER_SET_PROPS_RETURN_COUNT = "SET r += row.props\nRETURN count(r) as created"

CYPHER_GET_FUNCTION_SOURCE_LOCATION = """
MATCH (m:Module)-[:DEFINES]->(n)
WHERE id(n) = $node_id
RETURN n.qualified_name AS qualified_name, n.start_line AS start_line,
       n.end_line AS end_line, m.path AS path
"""

CYPHER_FIND_BY_QUALIFIED_NAME = """
MATCH (n) WHERE n.qualified_name = $qn
OPTIONAL MATCH (m:Module)-[*]-(n)
RETURN n.name AS name, n.start_line AS start, n.end_line AS end, m.path AS path, n.docstring AS docstring
LIMIT 1
"""


CYPHER_FIND_FORWARD_PATHS = """
MATCH path = (start:Function)-[:CALLS*1..5]->(end:Function)
WHERE start.name = $start_name
RETURN nodes(path) AS nodes, relationships(path) AS rels
LIMIT $limit
"""

CYPHER_FIND_BACKWARD_PATHS = """
MATCH path = (start:Function)-[:CALLS*1..5]->(end:Function)
WHERE start.name = $harness_name AND end.name = $sink_name
RETURN nodes(path) AS nodes, relationships(path) AS rels
LIMIT $limit
"""

CYPHER_FIND_FUNCTION_BY_LOCATION = """
MATCH (f:Function)
WHERE f.path ENDS WITH $path AND f.start_line <= $line AND f.end_line >= $line
RETURN f.qualified_name AS qualified_name, f.name AS name
LIMIT 1
"""

# Detailed path queries that return function metadata for building CodeSnippets
CYPHER_FIND_FORWARD_PATHS_DETAILED = """
MATCH path = (start:Function)-[:CALLS*1..10]->(end:Function)
WHERE start.name = $start_name
WITH path, nodes(path) AS ns
UNWIND ns AS n
OPTIONAL MATCH (m:Module)-[:DEFINES]->(n)
RETURN
  [x IN ns | x.qualified_name] AS path_qnames,
  [x IN ns | x.name] AS path_names,
  [x IN ns | x.start_line] AS path_start_lines,
  [x IN ns | x.end_line] AS path_end_lines,
  collect(DISTINCT m.path) AS module_paths
LIMIT $limit
"""

CYPHER_FIND_BACKWARD_PATHS_DETAILED = """
MATCH path = (start:Function)-[:CALLS*1..10]->(end:Function)
WHERE start.name = $harness_name AND end.name = $sink_name
WITH path, nodes(path) AS ns
UNWIND ns AS n
OPTIONAL MATCH (m:Module)-[:DEFINES]->(n)
RETURN
  [x IN ns | x.qualified_name] AS path_qnames,
  [x IN ns | x.name] AS path_names,
  [x IN ns | x.start_line] AS path_start_lines,
  [x IN ns | x.end_line] AS path_end_lines,
  collect(DISTINCT m.path) AS module_paths
LIMIT $limit
"""

# Find leaf functions (functions that are called but don't call others = potential sinks)
CYPHER_FIND_LEAF_FUNCTIONS = """
MATCH path = (start:Function)-[:CALLS*1..10]->(leaf:Function)
WHERE start.name = $start_name AND NOT (leaf)-[:CALLS]->(:Function)
OPTIONAL MATCH (m:Module)-[:DEFINES]->(leaf)
RETURN DISTINCT
  leaf.name AS name,
  leaf.qualified_name AS qualified_name,
  leaf.start_line AS start_line,
  leaf.end_line AS end_line,
  m.path AS path
LIMIT $limit
"""

# Lookup function by name (for resolving harness/sink names)
CYPHER_FIND_FUNCTION_BY_NAME = """
MATCH (f:Function)
WHERE f.name = $name
OPTIONAL MATCH (m:Module)-[:DEFINES]->(f)
RETURN
  f.name AS name,
  f.qualified_name AS qualified_name,
  f.start_line AS start_line,
  f.end_line AS end_line,
  m.path AS path
LIMIT $limit
"""

# Get callers of a function (reverse-call lookup)
CYPHER_GET_CALLERS = """
MATCH (caller:Function)-[:CALLS]->(target:Function)
WHERE target.name = $name
OPTIONAL MATCH (m:Module)-[:DEFINES]->(caller)
RETURN DISTINCT
  caller.name AS name,
  caller.qualified_name AS qualified_name,
  caller.start_line AS start_line,
  caller.end_line AS end_line,
  m.path AS path
LIMIT $limit
"""

# Get callees of a function
CYPHER_GET_CALLEES = """
MATCH (caller:Function)-[:CALLS]->(callee:Function)
WHERE caller.name = $name
OPTIONAL MATCH (m:Module)-[:DEFINES]->(callee)
RETURN DISTINCT
  callee.name AS name,
  callee.qualified_name AS qualified_name,
  callee.start_line AS start_line,
  callee.end_line AS end_line,
  m.path AS path
LIMIT $limit
"""

def wrap_with_unwind(query: str) -> str:
    return f"UNWIND $batch AS row\n{query}"


def build_nodes_by_ids_query(node_ids: list[int]) -> str:
    placeholders = ", ".join(f"${i}" for i in range(len(node_ids)))
    return f"""
MATCH (n)
WHERE id(n) IN [{placeholders}]
RETURN id(n) AS node_id, n.qualified_name AS qualified_name,
       labels(n) AS type, n.name AS name
ORDER BY n.qualified_name
"""


def build_constraint_query(label: str, prop: str) -> str:
    return f"CREATE CONSTRAINT ON (n:{label}) ASSERT n.{prop} IS UNIQUE;"


def build_index_query(label: str, prop: str) -> str:
    return f"CREATE INDEX ON :{label}({prop});"


def build_merge_node_query(label: str, id_key: str) -> str:
    return f"MERGE (n:{label} {{{id_key}: row.id}})\nSET n += row.props"


def build_merge_relationship_query(
    from_label: str,
    from_key: str,
    rel_type: str,
    to_label: str,
    to_key: str,
    has_props: bool = False,
) -> str:
    query = (
        f"MATCH (a:{from_label} {{{from_key}: row.from_val}}), "
        f"(b:{to_label} {{{to_key}: row.to_val}})\n"
        f"MERGE (a)-[r:{rel_type}]->(b)\n"
    )
    query += CYPHER_SET_PROPS_RETURN_COUNT if has_props else CYPHER_RETURN_COUNT
    return query
