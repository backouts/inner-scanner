from __future__ import annotations
import json

def set_path(d: dict, path: str, value):
    keys = path.split(".")
    cur = d
    for k in keys[:-1]:
        if k not in cur or cur[k] is None or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value

def parse_value(raw: str):
    raw = raw.strip()
    if raw == "":
        return ""
    try:
        return json.loads(raw)   
    except Exception:
        pass
    if "," in raw:
        return [x.strip() for x in raw.split(",") if x.strip()]
    return raw

def normalize_key(key: str) -> str:
    key = key.strip()

    key = key.replace(":", ".")

    if key == "note":
        return "meta.note"
    if key == "os_guess":
        return "meta.os_guess"

    return key

def register(scanner, state):

    def targets_cmd(args):
        sub = args[0].lower() if args else "list"
        handlers = {
            "add": add,
            "set": set_,
            "unset": unset,
            "list": list_,
            "show": show,
            "remove": remove,
            "rm": remove,
            "del": remove,
            "use": use,
        }
        fn = handlers.get(sub)
        if not fn:
            print("usage: targets [list|show|add|set|unset|remove]")
            return
        fn(args[1:])

    def add(_args):
        tid = input("id (required): ").strip()
        host = input("host (blank=skip): ").strip() or None
        url = input("url (blank=skip): ").strip() or None

        raw = {"id": tid, "host": host, "url": url}
        try:
            scanner.add_target(raw)
            print(f"[+] added target: {tid}")
        except Exception as e:
            print(f"[-] {e}")

    def set_(args):
        if len(args) < 2:
            print("usage: targets set <id> key=value [key=value ...]")
            return
        tid = args[0]
        pairs = args[1:]

        patch = {}
        for p in pairs:
            if "=" not in p:
                print(f"[-] need key=value: {p}")
                return
            key, val = p.split("=", 1)
            k = normalize_key(key)
            set_path(patch, k, parse_value(val))

        try:
            scanner.update_target(tid, patch)
            print(f"[+] updated target: {tid}")
        except Exception as e:
            print(f"[-] {e}")

    def unset(args):
        if len(args) < 2:
            print("usage: targets unset <id> key [key ...]")
            return
        tid = args[0]
        keys = [normalize_key(k) for k in args[1:]]
        patch = {"__unset__": keys}
        try:
            scanner.update_target(tid, patch)
            print(f"[+] unset fields: {tid}")
        except Exception as e:
            print(f"[-] {e}")

    def list_(_args):
        items = scanner.list_targets()
        state["target_candidates"] = [t.get("id") for t in items]

        if not items:
            print("(no targets)")
            return

        for i, t in enumerate(items):
            ident = t.get("host") or t.get("url") or "-"
            has_ssh = "Y" if (t.get("auth") or {}).get("ssh") else "N"
            print(f"[#{i}] {t.get('id')} | {t.get('type')} | {ident} | ssh={has_ssh}")

    def show(args):
        if not args:
            print("usage: targets show <id>")
            return
        tid = args[0]
        t = scanner.get_target(tid)
        if not t:
            print(f"[-] target not found: {tid}")
            return
        print(json.dumps(t, ensure_ascii=False, indent=2))
    
    def remove(args):
        if not args:
            print("usage: targets remove <id>")
            return

        tid = args[0]
        confirm = input(f"remove target '{tid}'? [y/N]: ").strip().lower()
        if confirm != "y":
            print("[*] cancelled")
            return

        try:
            scanner.remove_target(tid)
            print(f"[+] removed target: {tid}")
        except Exception as e:
            print(f"[-] {e}")
    
    def use(args):
        if not args:
            print("usage: targets use <id|#index>")
            return

        token = args[0].strip()

        if token.startswith("#"):
            if "target_candidates" not in state:
                print("[-] run 'targets list' first")
                return

            idx_str = token[1:]
            if not idx_str.isdigit():
                print(f"[-] invalid index: {token}")
                return

            idx = int(idx_str)
            candidates = state["target_candidates"]
            if idx < 0 or idx >= len(candidates):
                print(f"[-] invalid target index: {idx}")
                return

            tid = candidates[idx]
        else:
            # 기본은 항상 ID로 처리
            tid = token

        t = scanner.get_target(tid)
        if not t:
            print(f"[-] target not found: {tid}")
            return

        state["target_id"] = tid
        ident = t.get("host") or t.get("url") or "-"
        print(f"[*] using target: {tid} ({ident})")


    return targets_cmd
