#!/usr/bin/env python3
from argparse import ArgumentParser
from pathlib import Path
import ujson
from natsort import natsorted

from kellog import info, warning, error, debug

# ujson.dumps(d, indent=2, ensure_ascii=False, escape_forward_slashes=False, sort_keys=False)
# ==================================================================================================
def main(args):
	targets = [d for d in args.dir.glob("[0-9]" * 4 + "*") if d.is_dir()]
	paths = natsorted([p for d in targets for p in d.rglob("*") if p.suffix in [".jpg", ".mp4"]])
	for p in paths:
		debug(p)
	info(f"Found {len(paths)} files to sort")

	# Load JSON
	with open("game_IDs.json", "r") as file:
		json = ujson.load(file)

	gameList = []
	for path in paths:
		gameID = path.stem.split("-")[1]
		if gameID not in gameList:
			gameList.append(gameID)
	info(f"Identified {len(gameList)} different games")

	badChars = '<>:"/\|?*'
	for i, gameID in enumerate(gameList):
		try:
			name = json[gameID]
		except KeyError as e:
			error(f"No record for gameID `{gameID}` in `game_IDs.json")
			continue
		except:
			error("Some other error")
			error(f"Attempted gameID was `{gameID}`")
			continue

		info(f"{i + 1}/{len(gameList)}: {name}")
		for char in badChars:
			name = name.replace(char, "_")

		# Make directory, move files over while renaming
		(args.dir / name).mkdir(exist_ok=True)
		for path in natsorted([p for p in args.dir.rglob(f"*-{gameID}.*") if p.suffix in [".jpg", ".mp4"]]):
			n = path.stem.split(f"-")[0]
			n = f"{n[:4]}-{n[4:6]}-{n[6:8]}_{n[8:10]}-{n[10:12]}-{n[12:14]}"
			dest = (args.dir / name / n).with_suffix(path.suffix)
			if not dest.exists():
				path.replace(dest)
			else:
				error(f"Destination '{dest.relative_to(args.dir)}' exists when moving '{path.relative_to(args.dir)}'")

	# Remove old empty directories
	for directory in targets:
		if not clean_up(directory):
			warning(f"Not cleaning up '{directory}' as it still contains files")


# ==================================================================================================
def clean_up(directory):
	"""Remove a directory tree (if it's empty)."""
	assert directory.is_dir()
	clean = all([clean_up(c) for c in directory.glob("*") if c.is_dir()])
	if len(directory.glob("*")) == 0:
		debug(f"Deleting '{directory}', empty")
		directory.rmdir()
		return True
	return False


# ==================================================================================================
def parse_args():
	parser = ArgumentParser()
	parser.add_argument("--dir", "-d", type=str, metavar="PATH", default=Path.home() / "Pictures" / "Screenshots" / "Switch", help="Directory where the screenshots are stored")

	args = parser.parse_args()
	args.dir = Path(args.dir)

	return args


# ==================================================================================================
if __name__ == "__main__":
	main(parse_args())
