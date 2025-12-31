from inner.app.repl import repl

BANNER = r"""
 ██╗███╗   ██╗███╗   ██╗███████╗██████╗ 
 ██║████╗  ██║████╗  ██║██╔════╝██╔══██╗
 ██║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
 ██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
 ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
 ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝

  Engine : inner
  Team   : SK Shieldus Rookies 7 team
"""

def main():
    print(BANNER)
    repl()

if __name__ == "__main__":
    main()
