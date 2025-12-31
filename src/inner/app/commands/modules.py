from inner.plugins.registry import load_modules
import json
from rich.console import Console
from rich.table import Table

console = Console()

def _render_options_table(module, state):
    spec = module.MODULE.get("options", {})
    cur = state.get("options", {})

    table = Table(title="Options", show_lines=False)
    table.add_column("Name", style="bold")
    table.add_column("Type")
    table.add_column("Required")
    table.add_column("Current")
    table.add_column("Default")

    if not spec:
        console.print("[dim](no options)[/dim]")
        return

    for name, s in spec.items():
        typ = s.get("type", "str")
        default = s.get("default")
        required = s.get("required", False)
        current = cur.get(name, default)

        # 색 규칙
        row_style = None
        if required and (current is None or current == ""):
            row_style = "red"
        elif current != default:
            row_style = "yellow"

        table.add_row(
            name,
            typ,
            "yes" if required else "no",
            str(current),
            str(default),
            style=row_style,
        )

    console.print(table)

def _parse_value(raw: str):
    raw = raw.strip()
    if raw == "":
        return ""
    try:
        return json.loads(raw)  # 숫자/불리언/null/"문자열"
    except Exception:
        pass
    if "," in raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    return raw

def _coerce_type(val, typ: str):
    if typ == "str":
        return str(val)
    if typ == "int":
        if isinstance(val, bool):
            raise ValueError("int cannot be bool")
        return int(val)
    if typ == "bool":
        if isinstance(val, bool):
            return val
        if isinstance(val, str):
            s = val.strip().lower()
            if s in ("true","1","yes","y","on"): return True
            if s in ("false","0","no","n","off"): return False
        raise ValueError("bool must be true/false")
    if typ == "list[str]":
        if isinstance(val, list):
            return [str(x) for x in val]
        if isinstance(val, str):
            return [x.strip() for x in val.split(",") if x.strip()]
        raise ValueError("list[str] must be list or comma string")
    return val

def register(scanner, state):
    modules = load_modules()

    def _sorted_module_ids():
        return sorted(modules.keys())

    def modules_cmd(args):
        if not args:
            print("usage: modules [list|use]")
            return
        sub = args[0]

        if sub == "list":
            mids = _sorted_module_ids()
            state["module_candidates"] = mids

            for i, mid in enumerate(mids):
                name = modules[mid].MODULE.get("name")
                print(f"[{i}] {mid} : {name}")
            return

        if sub == "use":
            if len(args) < 2:
                print("usage: modules use <module_id>")
                return
            
            mid_arg = args[1].strip()
            candidates = state.get("module_candidates")
            if not candidates:
                candidates = _sorted_module_ids()

            if mid_arg.isdigit():
                idx = int(mid_arg)
                if idx < 0 or idx >= len(candidates):
                    print(f"[-] invalid module index: {idx}")
                    return
                mid = candidates[idx]
            else:
                mid = mid_arg

            if mid not in modules:
                print(f"[-] unknown module: {mid}")
                return
            state["module_id"] = mid
            state["options"] = {
                k: v.get("default")
                for k, v in modules[mid].MODULE.get("options", {}).items()
            }
            print(f"[*] using module: {mid}")
            return
        
        if sub in ("unuse", "clear"):
            if not state.get("module_id"):
                print("[*] no module in use")
                return

            state["module_id"] = None
            state["options"] = {}
            print("[*] module cleared")
            return
        
        if sub == "options":
            mid = state.get("module_id")
            if not mid:
                console.print("[red]no module in use. try: use <module_id>[/red]")
                return

            _render_options_table(modules[mid], state)
            return
        
        if sub == "set":
            mid = state.get("module_id")
            if not mid:
                print("[-] no module in use. try: use <module_id>")
                return
            if len(args) < 2:
                print("usage: set key=value [key=value ...]")
                return

            spec = modules[mid].MODULE.get("options", {})
            for p in args[1:]:
                if "=" not in p:
                    print(f"[-] need key=value: {p}")
                    return
                key, raw = p.split("=", 1)
                key = key.strip()

                if key not in spec:
                    print(f"[-] unknown option: {key}")
                    continue

                wanted = spec[key].get("type", "str")
                v = _parse_value(raw)
                v = _coerce_type(v, wanted)
                state["options"][key] = v

            print("[+] options updated")
            return
        
        if sub == "search":
            if len(args) < 2:
                print("usage: search <keyword>")
                return

            keyword = args[1].lower()
            mids = _sorted_module_ids()

            found = []
            for mid in mids:
                m = modules[mid]
                meta = m.MODULE
                hay = " ".join([
                    mid,
                    meta.get("name", ""),
                    meta.get("description", ""),
                    " ".join(meta.get("tags", [])),
                ]).lower()

                if keyword in hay:
                    found.append(mid)

            if not found:
                print("(no matching modules)")
                return
            
            state["module_candidates"] = found

            for i, mid in enumerate(found):
                name = modules[mid].MODULE.get("name")
                print(f"[{i}] {mid} : {name}")
            return

        print("usage: modules [list|use]")

    return modules_cmd
