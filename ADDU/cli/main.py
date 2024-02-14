from rich.console import Console
from rich.prompt import Prompt

from ADDU.cli.addu_panels import option_panel, about_panel, workspace_creation_panel, list_workspaces
from ADDU.logic import addu_docker_factory as dof


def main():
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
            main()
        case 'create':
            ws_name, image, user, distro, editor = workspace_creation_panel(console)
            dof.CreateWorkspace(console, ws_name, distro, user, image, editor)
        case 'list':
            console.print(list_workspaces())
            input("Enter to go back")
            console.clear()
            main()
        case 'run':
            console.print("WIP")
        case 'delete':
            console.print("WIP")
        case 'exit':
            console.print("[bold green]Goodbye![/bold green]")


if __name__ == '__main__':
    main()
