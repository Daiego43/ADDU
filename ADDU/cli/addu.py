import time

from rich.console import Console
from rich.prompt import Prompt

from ADDU.cli.addu_panels import (option_panel, about_panel, workspace_creation_panel,
                                  list_workspaces, delete_workspace, run_workspace)
from ADDU.logic import workspace as ws


def addu_cli():
    console = Console()
    options = option_panel()
    console.print(options)
    options = ['about', 'create', 'list', 'run', 'delete', "exit"]
    option = Prompt.ask("Choose an option", choices=options)
    console.clear()
    match option:
        case 'about':
            console.print(about_panel())
            input("Enter to go back")
            console.clear()
            addu_cli()
        case 'create':
            ws_name, base_image, user, distro, editor = workspace_creation_panel(console)
            workspace = ws.Workspace(ws_name, user, distro, base_image, editor)
            console.print("[bold blue]Creating workspace...[bold blue]")
            workspace.create_workspace()
            console.print(f"[bold green]Workspace {ws_name} created![/bold green]")
            console.print("[bold blue]Building image...[bold blue]")
            workspace.build_image()
            console.print(f"[bold green]Image built![/bold green]")
            time.sleep(1)
            console.clear()
            addu_cli()
        case 'list':
            console.print(list_workspaces())
            input("Enter to go back")
            console.clear()
            addu_cli()
        case 'run':
            run_workspace(console)
            console.clear()
            addu_cli()
        case 'delete':
            delete_workspace(console)
            console.clear()
            addu_cli()
        case 'exit':
            console.print("[bold green]Goodbye![/bold green]")


if __name__ == '__main__':
    addu_cli()
