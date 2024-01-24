import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask

def calculate_indices_and_lst(red_band_path, nir_band_path, thermal_band_path, output_path):
    # Open the red and NIR bands
    with rasterio.open(red_band_path) as red_src, rasterio.open(nir_band_path) as nir_src:
        # Read the bands
        red_band = red_src.read(1).astype('float64')
        nir_band = nir_src.read(1).astype('float64')
        

        # Calculate NDVI
        ndvi = np.where((nir_band + red_band) == 0, 0, (nir_band - red_band) / (nir_band + red_band))

        # Calculate the minimum and maximum NDVI
        ndvi_min = np.min(ndvi)
        print(ndvi_min)
        ndvi_max = np.max(ndvi)
        print(ndvi_max)

        # Calculate FV
        fv = ((ndvi - ndvi_min) / (ndvi_max - ndvi_min)) ** 2

        # Calculate EM
        em = 0.004 * fv + 0.986

        # Open the thermal band
        with rasterio.open(thermal_band_path) as thermal_src:
            # Read the thermal band
            thermal_band = thermal_src.read(1).astype('float64')
            print(thermal_band)

            # Convert DN to TOA brightness temperature in Kelvin
            ML = 0.003342  # Replace with your actual value
            AL = 146  # Replace with your actual value
            thermal_band = thermal_band * ML + AL

            # Mask no data values
            thermal_band[thermal_band == thermal_src.nodata] = np.nan

            # Calculate LST in Celsius / Celsius
            lst = thermal_band - 273.15 # (thermal_band / (1 + (0.00115 * (thermal_band / 1.438)) * np.log(em)))
            lst[lst < 0] = np.nan
        print(np.nanmin(lst))
        print(np.nanmax(lst))

        # Update the metadata
        meta = thermal_src.meta
        meta.update(dtype=rasterio.float32)

        # Write the LST to a new file
        with rasterio.open(output_path, 'w', **meta) as dst:
            dst.write(lst.astype(rasterio.float32), 1)

# Usage
calculate_indices_and_lst('2023/red_band.TIF', '2023/nir_band.TIF', '2023/ST_B10.TIF', 'lst_calc.tif')