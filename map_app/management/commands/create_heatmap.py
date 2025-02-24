import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from rasterio.transform import from_origin
from scipy.ndimage import gaussian_filter  # For smoothing
from map_app.models import Species, Grid, Results

class Command(BaseCommand):
    help = 'Generate heatmap raster from Results model data using posterior median values'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting raster generation...'))
        
        # Define the output directory and ensure it exists.
        output_dir = os.path.join('map_app', 'static', 'images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set the output raster file path.
        output_raster = os.path.join(output_dir, 'heatmap_raster.tif')
        
        self.create_heatmap_raster(output_raster)
        self.visualize_raster(output_raster)  # Visualize the raster.
        self.stdout.write(self.style.SUCCESS('Raster generation and visualization completed.'))

    def create_heatmap_raster(self, output_raster):
        # Query the Results table for grid coordinates and posterior median values.
        latitudes, longitudes, medians = [], [], []
        results = Results.objects.select_related('bird_speciesID', 'gridID').all()
        for result in results:
            grid = result.gridID
            latitudes.append(grid.Grid_Lat_NAD83)
            longitudes.append(grid.Grid_Long_NAD83)
            medians.append(result.posterior_median)

        # Define raster grid parameters.
        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lon, max_lon = min(longitudes), max(longitudes)
        pixel_size = 0.01  # Adjust as needed.
        nrows = int((max_lat - min_lat) / pixel_size) + 1
        ncols = int((max_lon - min_lon) / pixel_size) + 1
        raster_data = np.zeros((nrows, ncols), dtype=np.float32)

        # Use from_origin(min_lon, max_lat, pixel_size, pixel_size) for correct alignment.
        transform = from_origin(min_lon, max_lat, pixel_size, pixel_size)

        # Populate the raster with posterior median values.
        for lat, lon, median in zip(latitudes, longitudes, medians):
            row = int((max_lat - lat) / pixel_size)
            col = int((lon - min_lon) / pixel_size)
            raster_data[row, col] = median

        # Apply Gaussian smoothing (sigma=2.0) and boost intensity.
        raster_data = gaussian_filter(raster_data, sigma=2.0)
        raster_data = raster_data * 20  # Adjust multiplier as needed.

        # Write the smoothed/scaled raster to a GeoTIFF.
        with rasterio.open(
            output_raster, 'w', driver='GTiff', 
            height=nrows, width=ncols, count=1, dtype='float32',
            crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(raster_data, 1)

        self.stdout.write(self.style.SUCCESS(f"Raster file created at '{output_raster}'."))

    def visualize_raster(self, raster_file):
        # Open the raster file.
        with rasterio.open(raster_file) as src:
            data = src.read(1)

        # Mask out zero values.
        masked_data = np.ma.masked_equal(data, 0.0)

        # Normalize data to [0, 1].
        if masked_data.max() - masked_data.min() > 0:
            norm_data = (masked_data - masked_data.min()) / (masked_data.max() - masked_data.min())
        else:
            norm_data = masked_data

        # Clip values at the 95th percentile so that high intensities saturate to 1.
        thresh = np.percentile(norm_data.compressed(), 95)
        norm_data = np.clip(norm_data, 0, thresh)
        norm_data = norm_data / thresh

        # Use the colorblind-friendly 'viridis' colormap without transparency.
        cmap = plt.get_cmap('viridis').copy()
        # (Removed: cmap.set_bad(color=(0, 0, 0, 0)))

        # Display the heatmap with bilinear interpolation.
        plt.figure(figsize=(10, 6))
        plt.imshow(norm_data, cmap=cmap, interpolation='bilinear', vmin=0, vmax=1)
        plt.colorbar(label='Posterior Median (normalized)')
        plt.title('Heatmap from Raster using Posterior Median')
        plt.show()
