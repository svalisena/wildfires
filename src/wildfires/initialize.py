from nasa import earth
from typing import NamedTuple, Any
from tqdm import tqdm
import pendulum
import os

os.environ.setdefault(
    'NASA_API_KEY',
    'bp2Zqn5GgSe9PIhaRM4hgddtRbPqWBWIljeZKoEE',
)


class Shot(NamedTuple):
    """
    Represents a shot from Landsat. The asset is the output of the listing
    and the image contains details about the actual image.
    """

    asset: Any
    url: Any


MAX_CLOUD_SCORE = 0.5

class LandsatBisector:
    """
    Manages the different assets from landsat to facilitate the bisection
    algorithm.
    """

    def __init__(self, lon, lat):
        self.lon, self.lat = lon, lat
        self.shots = self.get_shots()

    @property
    def count(self):
        return len(self.shots)

    def get_shots(self):
        """
        Not all returned assets are useful (some have clouds). This function
        does some filtering in order to remove those useless assets and returns
        pre-computed shots which can be used more easily.
        """

        begin = '2000-01-01'
        end = pendulum.now('UTC').date().isoformat()

        assets = earth.assets(lat=self.lat, lon=self.lon, begin=begin, end=end)
        out = []

        for asset in tqdm(assets):
            img = asset.get_asset_image(cloud_score=True)

            if (img.cloud_score or 1.0) <= MAX_CLOUD_SCORE:
                out.append(Shot(asset, img.url))

        return out



