from __future__ import annotations
import json
from rich.console import Console
from rich.table import Table

from inner.core.storage.result_store import ResultStore

console = Console()

def register(scanner, state):
    store = ResultStore()

    def _render(items):
        if not items:
            console.print("[dim](no results)[/dim]")
            return

        table = Table(title="Results")
        table.add_column("#", justify="right")
        table.add_column("result_id", style="bold")
        table.add_column("status")
        table.add_column("severity")
        table.add_column("target")
        table.add_column("module")
        table.add_column("title")

        for i, r in enumerate(items):
            status = r.get("status", "")
            style = None
            if status == "FAIL":
                style = "red"
            elif status == "WARN":
                style = "yellow"
            elif status == "ERROR":
                style = "magenta"

            table.add_row(
                str(i),
                str(r.get("result_id", "")),
                str(status),
                str(r.get("severity", "")),
                str(r.get("target_id", "")),
                str(r.get("module_id", "")),
                str(r.get("title", "")),
                style=style,
            )
        console.print(table)

    def _parse_filters(args):
        # key=value 형태만 필터로
        filters = {}
        for p in args:
            if "=" not in p:
                console.print(f"[yellow]ignored[/yellow] {p} (use key=value)")
                continue
            k, v = p.split("=", 1)
            filters[k.strip()] = v.strip()
        return filters

    def _resolve_rid(token: str) -> str | None:
        # results list/search 직후 인덱스 지원
        candidates = state.get("result_candidates") or []
        if token.isdigit():
            idx = int(token)
            if idx < 0 or idx >= len(candidates):
                console.print(f"[red]invalid index:[/red] {idx}")
                return None
            return candidates[idx]
        return token

    def results_cmd(args):
        sub = args[0].lower() if args else "list"

        if sub == "list":
            filters = _parse_filters(args[1:])
            items = store.list(
                target_id=filters.get("target_id"),
                module_id=filters.get("module_id"),
                status=filters.get("status"),
                severity=filters.get("severity"),
            )
            state["result_candidates"] = [r.get("result_id") for r in items]
            _render(items)
            return

        if sub == "show":
            if len(args) < 2:
                console.print("[red]usage:[/red] results show <result_id|index>")
                return
            rid = _resolve_rid(args[1])
            if not rid:
                return

            for r in store.iter_all() or []:
                if r.get("result_id") == rid:
                    console.print_json(json.dumps(r, ensure_ascii=False, indent=2))
                    return
            console.print(f"[red]result not found:[/red] {rid}")
            return

        if sub == "search":
            if len(args) < 2:
                console.print("[red]usage:[/red] results search <keyword>")
                return
            kw = " ".join(args[1:]).lower()

            found = []
            for r in store.iter_all() or []:
                hay = " ".join([
                    str(r.get("result_id","")),
                    str(r.get("module_id","")),
                    str(r.get("target_id","")),
                    str(r.get("status","")),
                    str(r.get("severity","")),
                    str(r.get("title","")),
                    str(r.get("description","")),
                    " ".join(r.get("tags", []) or []),
                ]).lower()
                if kw in hay:
                    found.append(r)

            state["result_candidates"] = [r.get("result_id") for r in found]
            _render(found)
            return

        if sub in ("remove", "rm", "del"):
            if len(args) < 2:
                console.print("[red]usage:[/red] results remove <result_id|index>")
                return
            rid = _resolve_rid(args[1])
            if not rid:
                return

            confirm = input(f"remove result '{rid}'? [y/N]: ").strip().lower()
            if confirm != "y":
                console.print("[dim]cancelled[/dim]")
                return

            removed = store.remove_by_id(rid)
            if removed:
                console.print(f"[green][+] removed:[/green] {rid}")
            else:
                console.print(f"[yellow](not found)[/yellow] {rid}")
            return

        if sub == "clear":
            confirm = input("clear ALL results? [y/N]: ").strip().lower()
            if confirm != "y":
                console.print("[dim]cancelled[/dim]")
                return
            store.clear()
            state["result_candidates"] = []
            console.print("[green][+] cleared results[/green]")
            return

        console.print("[red]usage:[/red] results [list|show|search|remove|clear]")

    return results_cmd
