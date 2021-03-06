import urllib.request
from pathlib import Path
from threading import Thread

from tqdm import tqdm


default_models = {
    "encoder": ("https://drive.google.com/uc?export=download&id=1q8mEGwCkFy23KZsinbuvdKAQLqNKbYf1", 17090379),
    # Too large to put on google drive with a direct link...
    "synthesizer": ("https://www.dropbox.com/s/r37koa6ho5prz7w/synthesizer.pt?dl=1", 370554559),
    "vocoder": ("https://drive.google.com/uc?export=download&id=1cf2NO6FtI0jDuy8AV3Xgn6leO6dHjIgu", 53845290),
}


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download(url: str, target: Path, bar_pos=0):
    # Ensure the directory exists
    target.parent.mkdir(exist_ok=True, parents=True)

    desc = f"Downloading {target.name}"
    with DownloadProgressBar(unit="B", unit_scale=True, miniters=1, desc=desc, position=bar_pos, leave=False) as t:
        urllib.request.urlretrieve(url, filename=target, reporthook=t.update_to)


def ensure_default_models(models_dir: Path):
    # Define download tasks
    jobs = []
    for model_name, (url, size) in default_models.items():
        target_path = models_dir / "default" / f"{model_name}.pt"
        if target_path.exists():
            if target_path.stat().st_size != size:
                print(f"File {target_path} is not of expected size, redownloading...")
            else:
                continue

        thread = Thread(target=download, args=(url, target_path, len(jobs)))
        thread.start()
        jobs.append((thread, target_path, size))

    # Run and join threads
    for thread, target_path, size in jobs:
        thread.join()

        assert target_path.stat().st_size == size, \
            f"Download for {target_path.name} failed. You may download models manually instead. Open an issue if the " \
            f"problem is recurrent.\nhttps://drive.google.com/drive/folders/1fU6umc5uQAVR2udZdHX-lDgXYzTyqG_j"
