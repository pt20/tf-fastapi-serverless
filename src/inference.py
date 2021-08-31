import math
import sys
from typing import Dict

import mercantile
import numpy as np
import rasterio as rio
import tensorflow as tf
from geojson_pydantic.features import Feature, FeatureCollection
from rasterio.crs import CRS
from rasterio.plot import reshape_as_image
from rio_tiler.io import COGReader
from shapely.geometry import box as shapely_box
from shapely.geometry import shape

sys.stdout.flush()
# np.set_printoptions(suppress=True)
model_path = "model/windturbine_floydhub.h5"
model = tf.keras.models.load_model(model_path)


# tif_uri = "model/m_4011125_sw_12_1_20110720.tif"
tif_uri = "https://naipeuwest.blob.core.windows.net/naip/v002/ut/2011/ut_100cm_2011/40111/m_4011125_sw_12_1_20110720.tif"
aoi2 = Feature(
    geometry={
        "type": "Polygon",
        "coordinates": [
            [
                [-111.98862075805664, 40.52658747242724],
                [-111.97969436645508, 40.51171103483292],
                [-111.95102691650389, 40.50975336307896],
                [-111.9455337524414, 40.5217595168077],
                [-111.96063995361328, 40.54628714504034],
                [-111.9807243347168, 40.542112863677644],
                [-111.98862075805664, 40.52658747242724],
            ]
        ],
    }
)


def run_model(image: np.ndarray) -> np.ndarray:
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 256, 256, 3), dtype=np.float32)

    # resize the image to a 256x256 with the same strategy as in TM2:
    # resizing the image to be at least 256x256 and then cropping from the center
    # size = (256, 256)
    # image = ImageOps.fit(image, size, Image.ANTIALIAS)
    print(image.shape)

    # turn the image into a numpy array
    image_array = np.asarray(image)

    # Normalize the image
    # normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    normalized_image_array = image_array.astype(np.float32) / 255.0

    # Load the image into the array
    data[0] = normalized_image_array

    # run the inference
    prediction = model.predict(data)
    return prediction


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return [lat_deg, lon_deg]


def run_prediction_for_aoi(aoi: Dict, tif_uri: str = tif_uri) -> FeatureCollection:
    with COGReader(tif_uri) as cog:
        geom_dict = aoi
        print("=" * 20, flush=True)
        print(geom_dict, flush=True)
        print("=" * 20, flush=True)
        img = cog.feature(geom_dict)

        tiles = mercantile.tiles(*img.bounds, [16])

        fc = []
        for tile in tiles:
            print(tile)
            data = reshape_as_image(cog.tile(*tile).data)[:, :, :3]

            # coords = num2deg(tile.x, tile.y, tile.z)
            tile_bounds = cog.tile(*tile).bounds
            trans_tile_bounds = rio.warp.transform_bounds(
                CRS.from_epsg(3857), CRS.from_epsg(4326), *tile_bounds
            )

            tile_shp = shapely_box(*trans_tile_bounds)
            aoi_shp = shape(geom_dict)

            # this part checks for the tile intersection with original AOI
            # and runs the inference only when it intersecting
            # this way we save some computing resources
            if aoi_shp.intersects(tile_shp):
                output = run_model(data)
                is_windturbine = True if output[0][0] > 0.5 else False

                feat = Feature(
                    id=f"{tile.x}_{tile.y}_{tile.z}",
                    geometry=tile_shp,
                    properties={"windtrubine": is_windturbine},
                )

                fc.append(feat)

    return FeatureCollection(features=fc)


# import geojson

# fc = run_prediction_for_aoi()
# with open("model/bleh.geojson", "w") as fp:
#     geojson.dump(fc.dict(), fp)
