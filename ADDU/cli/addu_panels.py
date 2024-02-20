import os
import shutil
import yaml

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.table import Table

from pathlib import Path

current_file_path = Path(__file__).parent
config_path = current_file_path / ".." / "config" / "config.yaml"
config_path = config_path.resolve()

CONFIG = yaml.load(open(config_path, "r"), Loader=yaml.FullLoader)
workspaces_path = Path(CONFIG["addu-workspaces-path"]).expanduser()
if not os.path.exists(workspaces_path):
    os.makedirs(workspaces_path)


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
        Text("about  -  About ADDU\n", "grey"),
        Text("create -  Create a workspace\n", "blue"),
        Text("list   -  List workspaces\n", "bold yellow"),
        Text("run    -  Run a workspace\n", "bold green"),
        Text("delete -  Delete a workspace\n", "bold red"),
        Text("exit   -  Exit ADDU cli\n", "bold purple"),
    )
    return Panel.fit(opciones, title=":whale: ADDU :whale:", border_style="cyan", subtitle="A Dumb Docker User",
                     padding=(1, 2))


def workspace_creation_panel(console):
    config = CONFIG
    ws_name = Prompt.ask("[green]Workspace name[/green]")
    distro = Prompt.ask("[green]Choose a ROS distro[/green]", choices=config["ros-distros"].keys())
    console.print(f"[bold green]Available images for {distro}[/bold green]")
    for i, image in enumerate(config["ros-distros"][distro]):
        console.print(f" {i} - [cyan]{image}[/cyan]")
    image = Prompt.ask("[green]Choose an image[/green]",
                       choices=[str(i) for i in range(len(config["ros-distros"][distro]))])
    user = Prompt.ask("[green]Provide a username for the image[/green]")
    console.print(f"[bold green]Available editors[/bold green]")
    for i, editor in enumerate(config["supported-editors"]):
        console.print(f" {i} - [cyan]{editor}[/cyan]")
    editor = Prompt.ask("[green]Choose an editor[/green]",
                        choices=[str(i) for i in range(len(config["supported-editors"]))])
    editor = config["supported-editors"][int(editor)]
    image = config["ros-distros"][distro][int(image)]
    console.clear()
    return ws_name, image, user, distro, editor


def list_workspaces():
    title = Text("Workspaces", "bold")
    subtitle = Text("Workspaces", "bold")
    workspaces_path = Path(CONFIG["addu-workspaces-path"]).expanduser()
    workspaces = os.listdir(workspaces_path)
    table = Table()
    table.add_column("ID", style="cyan")
    table.add_column("Workspace", style="magenta")
    table.add_column("Distro", style="green")
    table.add_column("User", style="blue")
    table.add_column("Image name", style="red")
    if not workspaces:
        return Panel.fit("No workspaces found!", title=title, border_style="blue", subtitle=subtitle, padding=(1, 2))

    for i, ws in enumerate(workspaces):
        ws_config = yaml.load(open(f"{workspaces_path}/{ws}/config.yaml", "r"), Loader=yaml.FullLoader)
        table.add_row(str(i), ws, ws_config["distro"], ws_config["user"], ws_config["base_image"])

    return Panel.fit(table, title=title, border_style="blue", subtitle=subtitle, padding=(1, 2))


def delete_workspace(console):
    list_panel = list_workspaces()
    workspaces_path = Path(CONFIG["addu-workspaces-path"]).expanduser()
    workspaces = os.listdir(workspaces_path)
    console.print(list_panel)
    if not workspaces:
        return
    i = Prompt.ask("Enter the workspace id you want to delete", choices=[str(i) for i in range(len(workspaces))])
    path = workspaces_path / workspaces[int(i)]
    shutil.rmtree(path)


def run_workspace(console):
    list_panel = list_workspaces()
    workspaces_path = Path(CONFIG["addu-workspaces-path"]).expanduser()
    workspaces = os.listdir(workspaces_path)
    console.print(list_panel)
    if not workspaces:
        return
    i = Prompt.ask("Enter the workspace id you want to run", choices=[str(i) for i in range(len(workspaces))])
    ws = workspaces[int(i)]
    os.system(f"bash {workspaces_path}/{ws}/startup.sh")
