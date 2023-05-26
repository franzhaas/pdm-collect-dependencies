from pdm.cli.commands.base import BaseCommand
from pdm.project.config import ConfigItem
import itertools
import unearth
import hashlib


def collect_dependencies(core):
    core.register_command(CollectDependencies, "collect_dependencies")

class CollectDependencies(BaseCommand):
    """"""
    def add_arguments(self, parser):
        parser.add_argument("-d", "--collect_dependencies_dir", help="Directory to collect the wheels in.")
        parser.add_argument("-w", "--which_wheels", default="first", help="Directory to collect the wheels in.")

    def handle(self, project, options):
        target_dir = options.collect_dependencies_dir
        files = project.lockfile["metadata"]["files"]
        pf = unearth.PackageFinder(index_urls=[item.url for item in project.sources])
        
        def _collector(files):
            for node in files.values():
                for item in node:
                    if item["url"][-3:]=="whl":
                        yield item["url"], item["hash"] 
                        if not options.which_wheels == "all":
                            break
                      
        
        links = ((unearth.Link(item[0]), item[1]) for item in _collector(files))
        with project.environment.get_finder(ignore_compatibility=True) as pf: 
            for current_link, hash in  links:
                wpath = pf.download_and_unpack(current_link, target_dir, target_dir)
                with open(wpath, "rb") as f:
                    hashtype, hashval = hash.split(":")
                    h = hashlib.new(hashtype)
                    h.update(f.read())
                digest = h.hexdigest()
                if hashval != digest:
                    project.core.ui.echo("ERROR: hash mismatch", style="error")
                    exit(1)
        project.core.ui.echo("Collected all wheels...", style="success")
