from rich.console import Console
from inner.core.result_schema import validate_result, ResultSchemaError
from inner.core.storage.result_store import ResultStore
from inner.core.clients.http import HttpClient

console = Console()

def register(scanner, state):
    def run_cmd(args):
        mid = state.get("module_id")
        if not mid:
            console.print("[red]no module in use[/red]")
            return

        target_id = state.get("target_id")
        target = scanner.get_target(target_id) if target_id else None

        module = scanner.get_module(mid)
        spec = module.MODULE.get("options", {})
        opts = state.get("options", {})

        missing = [
            k for k, s in spec.items()
            if s.get("required") and (opts.get(k) in (None, ""))
        ]
        if missing:
            console.print(f"[red]missing required options: {', '.join(missing)}[/red]")
            return

        console.print(f"[bold cyan][*] running module {mid}[/bold cyan]")

        store = ResultStore()
        http_client = HttpClient(
            timeout=opts.get("timeout", 5),
        )

        ctx = {
            "target": target,
            "options": opts,
            "artifacts": store.aggregate_artifacts(target_id) if target_id else {},
            "meta": {
                "module_id": mid,
            },
            "clients": {
                "http": http_client
            },
        }

        result = module.run(ctx)


        try:
            validate_result(result)
        except ResultSchemaError as e:
            console.print(f"[red]invalid result schema:[/red] {e}")
            return

        if not result:
            console.print("[dim](no result)[/dim]")
            return
        
        try:
            store.append(result)
        except ResultSchemaError as e:
            console.print(f"[red]invalid result schema:[/red] {e}")
            return

        console.print(result)
        console.print("[green][+] result stored[/green]")
        console.print("[green][+] module finished[/green]")

    return run_cmd
