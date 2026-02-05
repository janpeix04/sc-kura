from app.api.main import router


class RouteNode:
    def __init__(self):
        self.children: dict[str, RouteNode] = {}
        self.param: RouteNode | None = None
        self.methods: dict[str, str] = {}  # method -> full path


def insert(root: RouteNode, path: str, methods: set) -> list[str]:
    parts = [p for p in path.split("/") if p]
    node = root
    parent = None
    last_is_param = False
    conflicts: list[str] = []

    for part in parts:
        parent = node
        last_is_param = part.startswith("{") and part.endswith("}")
        if last_is_param:
            if not node.param:
                node.param = RouteNode()
            node = node.param
        else:
            node = node.children.setdefault(part, RouteNode())

    # Duplicates
    for m in methods:
        if m in node.methods:
            conflicts.append(f"Duplicate {m}: {path} vs {node.methods[m]}")
        node.methods[m] = path

    # Shadowing
    if parent and not last_is_param and parent.param:
        for m in methods:
            if m in parent.param.methods:
                conflicts.append(f"Shadow {m}: {path} vs {parent.param.methods[m]}")

    return conflicts


def test_endpoint_clashes():
    root = RouteNode()
    conflicts: list[str] = []

    for route in router.routes:
        conflicts.extend(insert(root, route.path, set(route.methods)))

    assert not conflicts, "\n".join(conflicts)
