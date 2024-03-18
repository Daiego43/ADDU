import time

from rich.console import Console
from rich.prompt import Prompt

from ADDU.cli.addu_panels import (option_panel,
                                  about_panel,
                                  workspace_creation_panel,
                                  list_workspaces_panel,
                                  delete_workspace_panel,
                                  run_workspace_panel,
                                  export_workspace_panel,
                                  import_workspace_panel)
from ADDU.logic.actions import (create_workspace,
                                run_workspace,
                                delete_workspace,
                                export_workspace,
                                import_workspace)


def addu_cli():
    console = Console()
    option_panel()
    options = ['about', 'create', 'list', 'run', 'delete', "export", "import", "exit"]
    option = Prompt.ask("Choose an option", choices=options)
    console.clear()
    match option:
        case 'about':
            about_panel()
            input("Enter to go back")
            console.clear()
            addu_cli()
        case 'create':
            ws_name, base_image, user, distro, editor = workspace_creation_panel()
            create_workspace(ws_name, user, distro, base_image, editor)
            time.sleep(2)
            console.clear()
            addu_cli()
        case 'list':
            list_workspaces_panel()
            input("Enter to go back")
            console.clear()
            addu_cli()
        case 'run':
            ws_name = run_workspace_panel()
            run_workspace(ws_name)
            console.clear()
            addu_cli()
        case 'delete':
            ws_path = delete_workspace_panel()
            delete_workspace(ws_path)
            console.clear()
            addu_cli()
        case 'export':
            ws_name = export_workspace_panel()
            export_workspace(ws_name)
            console.clear()
            addu_cli()
        case 'import':
            ws_name = import_workspace_panel()
            import_workspace(ws_name)
            console.clear()
            addu_cli()
        case 'exit':
            console.print("[bold green]Goodbye![/bold green]")


if __name__ == '__main__':
    addu_cli()
