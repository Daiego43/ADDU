import os

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text

print(os.getcwd())

CONFIG = yaml.load(open("ADDU/config/config.yaml", "r"), Loader=yaml.FullLoader)


def about_panel():
    titulo = Text("ADDU ", "bold")
    subtitle = "A Dumb Docker User"
    descripcion = Text.assemble(
        Text("ADDU is a creation and management tool of "),
        Text("ROS development environments.\n", "bold green"),
        Text("With ADDU you can run your favorite editor inside a container with all ROS dependencies installed.\n\n"),
        Text("\n\n Maintained by: Daiego43"),
    )
    descripcion.justify = "center"
    return Panel.fit(descripcion, title=titulo, border_style="blue", subtitle=subtitle, padding=(1, 2))


def option_panel():
    opciones = Text.assemble(
        Text("about - About ADDU\n", "grey"),
        Text("create -  Create a workspace\n", "blue"),
        Text("list   -  List workspaces\n", "bold yellow"),
        Text("run    -  Run a workspace\n", "bold green"),
        Text("delete -  Delete a workspace\n", "bold red"),
        Text("exit   -  Exit ADDU cli\n", "bold purple"),
    )
    return Panel.fit(opciones, title=":whale: ADDU :whale:", border_style="cyan", subtitle="A Dumb Docker User", padding=(1, 2))


def workspace_creation_panel(console):
    config = CONFIG
    ws_name = Prompt.ask("[green]Workspace name[/green]")
    distro = Prompt.ask("[green]Choose a ROS distro[/green]", choices=config["ros-distros"].keys())
    console.print(f"[bold green]Available images for {distro}[/bold green]")
    for i, image in enumerate(config["ros-distros"][distro]):
        console.print(f" {i} - [cyan]{image}[/cyan]")
    image = Prompt.ask("[green]Choose an image[/green]", choices=[str(i) for i in range(len(config["ros-distros"][distro]))])
    user = Prompt.ask("[green]Provide a username for the image[/green]")
    console.print(f"[bold green]Available editors[/bold green]")
    for i, editor in enumerate(config["supported-editors"]):
        console.print(f" {i} - [cyan]{editor}[/cyan]")
    editor = Prompt.ask("[green]Choose an editor[/green]", choices=[str(i) for i in range(len(config["supported-editors"]))])
    editor = config["supported-editors"][int(editor)]
    image = config["ros-distros"][distro][int(image)]
    console.clear()
    return ws_name, image, user, distro, editor


def list_workspaces():
    title = Text("Workspaces", "bold")
    subtitle = Text("Workspaces", "bold")
    workspaces = os.listdir(CONFIG["addu-workspaces-path"])
    content = Text.assemble([Text(f"{i} - {ws}") for i, ws in enumerate(workspaces)])
    return Panel.fit(content, title=title, border_style="blue", subtitle=subtitle, padding=(1, 2))

def delete_workspace():
    list_panel = list_workspaces()
    workspaces = os.listdir(CONFIG["addu-workspaces-path"])

    Prompt.ask("Enter the number of the workspace you want to delete")
    return list_panel

def test(panel):
    console = Console()
    console.print(panel)


if __name__ == '__main__':
    console = Console()
    workspace_creation_panel(console)
    print("Done")
