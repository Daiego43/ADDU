from ADDU.logic import workspace as ws
from rich.console import Console
import yaml
from pathlib import Path
import os
import shutil
import zipfile

current_file_path = Path(__file__).parent
config_path = current_file_path / ".." / "config" / "config.yaml"
config_path = config_path.resolve()
CONFIG = yaml.load(open(config_path, "r"), Loader=yaml.FullLoader)
workspaces_path = Path(CONFIG["addu-workspaces-path"]).expanduser()


def create_workspace(ws_name, user, distro, base_image, editor):
    console = Console()
    workspace = ws.Workspace(ws_name, user, distro, base_image, editor)
    console.print("[bold blue]Creating workspace...[bold blue]", end="")
    workspace.create_workspace()
    console.print(f"[bold green]Workspace {ws_name} created![/bold green]")
    console.print("[bold blue]Building image...[bold blue]", end="")
    workspace.build_image()
    console.print(f"[bold green]Image built![/bold green]")
    console.print("[bold blue]Dangling images are being removed[bold blue]")
    workspace.clean_up_build()


def list_worspaces():
    workspaces = os.listdir(workspaces_path)
    print(workspaces)


def run_workspace(ws_name):
    os.system(f"bash {workspaces_path}/{ws_name}/startup.sh")


def delete_workspace(path):
    shutil.rmtree(path)


def export_workspace(ws_name):
    shutil.make_archive(ws_name, 'zip', workspaces_path / ws_name)


def import_workspace(ruta_zip):
    archivo_zip = Path(ruta_zip)
    ruta_destino = Path(workspaces_path).expanduser() / archivo_zip.name.split(".")[0]
    with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
        zip_ref.extractall(ruta_destino)

    Console().print("[bold green]Workspace imported![/bold green]")


if __name__ == '__main__':
    export_workspace("test")
    import_workspace("test.zip")
