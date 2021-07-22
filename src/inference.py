import math

import geojson
import mercantile
import numpy as np
import tensorflow as tf
from aiocogeo import COGReader
from geojson import Feature, Point
from PIL import Image, ImageOps

np.set_printoptions(suppress=True)
model_path = "model/windturbine_floydhub.h5"
model = tf.keras.models.load_model(model_path)

# https://up42test.s3.amazonaws.com/aus_cogs/aus_id_2.tif


def get_tiles_xyz_from_cog(cog: COGReader):
    maxtrix_set = cog.create_tile_matrix_set()
    print(maxtrix_set)

    for row in maxtrix_set["tileMatrix"]:
        z = len(maxtrix_set) - int(row["identifier"])

        for x in range(row["matrixWidth"]):
            for y in range(row["matrixHeight"]):
                yield (x, y, z)


def get_cog_tile_bounds(x: int, y: int, z: int, cog: COGReader):
    ifd = cog.ifds[z]

    width = ifd.ImageWidth.value
    height = ifd.ImageHeight.value

    x_count = ifd.tile_count[0]
    y_count = ifd.tile_count[1]

    total_width = ifd.TileWidth.value * x_count
    total_height = ifd.TileHeight.value * y_count

    x_magnifier = total_width / width
    y_magnifier = total_height / height

    min_x, min_y, max_x, max_y = cog.native_bounds

    total_max_x = min_x + (max_x - min_x) * x_magnifier
    total_max_y = min_y + (max_y - min_y) * y_magnifier

    total_x_length = total_max_x - min_x
    total_y_length = total_max_y - min_y

    tile_min_x = min_x + (total_x_length * (x / x_count))
    tile_min_y = max_y - (total_y_length * (y / y_count))
    tile_max_x = min_x + (total_x_length * ((x + 1) / x_count))
    tile_max_y = max_y - (total_y_length * ((y + 1) / y_count))

    return tile_min_x, tile_min_y, tile_max_x, tile_max_y


async def get_cog_tiles_on_zoom(cog: COGReader, zoom: int):
    print("get_cog_tiles_on_zoom")
    min_x, min_y, max_x, max_y = cog.native_bounds

    west, south = mercantile.lnglat(min_x, min_y)
    east, north = mercantile.lnglat(max_x, max_y)

    tiles = mercantile.tiles(west, south, east, north, [zoom])
    print("=" * 20)
    print(len(list(tiles)))
    print("=" * 20)

    for tile in tiles:
        print("what's happening here?")
        # if idx < 50:
        data = await cog.read(bounds=mercantile.xy_bounds(*tile), shape=(256, 256))
        print("what's happening here?")
        yield tile, data


def get_image_from_cog_tile(tile):
    transposed = np.array(
        [
            tile[0].transpose(),
            tile[1].transpose(),
            tile[2].transpose(),
        ]
    )
    return Image.fromarray(transposed.transpose())


async def save_tiles_from_cog(cog: COGReader):
    for x, y, z in get_tiles_xyz_from_cog(cog):
        print(x, y, z)
        try:
            tile = await cog.get_tile(x, y, z)

            # Print tile POLYGON
            minx, miny, maxx, maxy = get_cog_tile_bounds(x, y, z, cog)
            print(
                f"POLYGON(({minx} {miny}, {minx} {maxy},"
                f" {maxx} {maxy}, {maxx} {miny}))"
            )

            if np.any(tile):
                image = get_image_from_cog_tile(tile)
                image.save(f"cog_tiles/{z}_{x}_{y}.png")
                print("saved")

        except Exception:
            print("Error while reading tile")


async def save_tiles_for_zoom(cog: COGReader, zoom: int, to_file: bool = False):
    fc = []
    async for tile, data in get_cog_tiles_on_zoom(cog, zoom):

        if np.any(data):
            image = get_image_from_cog_tile(data)

            output = run_model(image)
            windturbine = True if output[0][0] > 0.5 else False
            # other = output[0][1]

            coords = num2deg(tile.x, tile.y, tile.z)

            # feat = Point((coords[0], coords[1]))
            feat = Feature(
                geometry=Point((coords[1], coords[0])),
                properties={"windtrubine": windturbine},
            )

            fc.append(feat)

    if to_file:
        with open("my.geojson", "w") as fp:
            geojson.dump(fc, fp)

    return geojson.FeatureCollection(fc)


def run_model(image):
    # Create the array of the right shape to feed into the keras model
    # The 'length' or number of images you can put into the array is
    # determined by the first position in the shape tuple, in this case 1.
    data = np.ndarray(shape=(1, 256, 256, 3), dtype=np.float32)

    # resize the image to a 224x224 with the same strategy as in TM2:
    # resizing the image to be at least 224x224 and then cropping from the center
    size = (256, 256)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)

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


# import asyncio

# async def main():
#     URL = "https://up42test.s3.amazonaws.com/aus_1_cog.tif"
#     async with COGReader(URL) as cog:
#         fc = await save_tiles_for_zoom(cog, 18)


# asyncio.run(main())
