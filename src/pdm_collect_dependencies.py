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

    def handle(self, project, options):
        target_dir = options.collect_dependencies_dir
        files = project.lockfile["metadata"]["files"]
        pf = unearth.PackageFinder(index_urls=[item["url"] for item in project.sources])
        urls = ((item["url"], item["hash"]) for item in itertools.chain.from_iterable(files.values()))
        urls = (item for item in urls if item[0][-3:]=="whl")
        urls = (item for item in urls if item[0][:4]=="http")
        links = ((unearth.Link(item[0]), item[1]) for item in urls)
        for current_link, hash in  links:
            wpath = pf.download_and_unpack(current_link, target_dir, target_dir)
            with open(wpath, "rb") as f:
                hashtype, hashval = hash.split(":")
                h = hashlib.new(hashtype)
                h.update(f.read())
            digest = h.hexdigest()
            if hashval != digest:
                print("ERROR: hash mismatch")
                exit(1)