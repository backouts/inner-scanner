from inner.core.scanner import Scanner
from inner.app.commands.targets import register as register_targets
from inner.app.commands.modules import register as register_modules
from inner.app.commands.run import register as register_run
from inner.app.commands.results import register as register_results

def repl():
    scanner = Scanner()
    state = {
        "target_id": None, 
        "module_id": None, 
        "options": {},
        "module_candidates": None,
        }

    def cmd_help(args):
        print("help, exit, targets ...")

    def cmd_exit(args):
        raise SystemExit

    cmd_targets = register_targets(scanner, state)
    cmd_modules = register_modules(scanner, state)
    cmd_run = register_run(scanner, state)
    cmd_results = register_results(scanner, state)

    commands = {
        "help": cmd_help,
        "exit": cmd_exit,
        "quit": cmd_exit,
        "targets": cmd_targets,
        "modules": cmd_modules,
        "use": lambda args: cmd_modules(["use"] + args),
        "unuse": lambda args: cmd_modules(["unuse"]),
        "clear": lambda args: cmd_modules(["clear"]),
        "set": lambda args: cmd_modules(["set"] + args),
        "options": lambda args: cmd_modules(["options"] + args),
        "list": lambda args: cmd_modules(["list"] + args),
        "search": lambda args: cmd_modules(["search"] + args),
        "run": cmd_run,
        "results": cmd_results,
        "result": cmd_results,

    }

    while True:
        try:
            prompt = "inner"
            if state.get("target_id"):
                prompt += f"[{state['target_id']}]"
            if state.get("module_id"):
                prompt += f"[{state['module_id']}]"
            line = input(f"{prompt} > ").strip()

            if not line:
                continue
            parts = line.split()
            cmd, args = parts[0].lower(), parts[1:]
            fn = commands.get(cmd)
            if not fn:
                print("unknown command")
                continue
            fn(args)
        except KeyboardInterrupt:    
                print("\n" + "exit...")
                break
        except SystemExit:
            print("exit...")
            break
        except Exception as e:
            print(f"[-] {e}")
