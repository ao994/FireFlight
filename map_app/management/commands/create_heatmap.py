import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from rasterio.transform import from_origin
from matplotlib.colors import LinearSegmentedColormap
from map_app.models import Species, Grid, Results

class Command(BaseCommand):
    help = 'Generate heatmap raster from Results model data using posterior median values'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting raster generation...'))
        
        # Define the output directory and ensure it exists.
        output_dir = os.path.join('map_app', 'static', 'images')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Set the output raster file path within the static images folder.
        output_raster = os.path.join(output_dir, 'heatmap_raster.tif')
        
        self.create_heatmap_raster(output_raster)
        self.visualize_raster(output_raster)  # Visualize the raster from the static images folder.
        self.stdout.write(self.style.SUCCESS('Raster generation and visualization completed.'))

    def create_heatmap_raster(self, output_raster):
        # Query the Results table to get grid coordinates and posterior median values.
        latitudes = []
        longitudes = []
        medians = []

        results = Results.objects.select_related('bird_speciesID', 'gridID').all()

        for result in results:
            grid = result.gridID
            lat = grid.Grid_Lat_NAD83
            lon = grid.Grid_Long_NAD83
            median = result.posterior_median  # Using posterior median values.
            latitudes.append(lat)
            longitudes.append(lon)
            medians.append(median)

        # Setup the raster grid parameters.
        min_lat = min(latitudes)
        max_lat = max(latitudes)
        min_lon = min(longitudes)
        max_lon = max(longitudes)
        pixel_size = 0.01  # Adjust the pixel size as necessary.

        nrows = int((max_lat - min_lat) / pixel_size) + 1
        ncols = int((max_lon - min_lon) / pixel_size) + 1
        raster_data = np.zeros((nrows, ncols), dtype=np.float32)

        # Define the geospatial transform for the raster.
        transform = from_origin(max_lon, min_lat + pixel_size, pixel_size, pixel_size)

        # Fill the raster with posterior median values.
        for lat, lon, median in zip(latitudes, longitudes, medians):
            row = int((max_lat - lat) / pixel_size)
            col = int((lon - min_lon) / pixel_size)
            raster_data[row, col] = median

        # Write the raster data to a GeoTIFF file in the static images folder.
        with rasterio.open(
            output_raster, 'w', driver='GTiff', 
            height=nrows, width=ncols, count=1, dtype='float32',
            crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(raster_data, 1)

        self.stdout.write(self.style.SUCCESS(f"Raster file created at '{output_raster}'."))

    def visualize_raster(self, raster_file):
        # Open the raster file from the static images folder.
        with rasterio.open(raster_file) as src:
            data = src.read(1)  # Read the first (and only) band.

        # Mask the data where values are 0.0 so they appear transparent.
        masked_data = np.ma.masked_equal(data, 0.0)

        # Create a copy of the 'cividis' colormap and set the masked ('bad') values to be transparent.
        cmap = plt.get_cmap('cividis').copy()
        cmap.set_bad(color=(0, 0, 0, 0))  # Fully transparent RGBA tuple

        # Plot the raster data using matplotlib.
        plt.figure(figsize=(10, 6))
        plt.imshow(masked_data, cmap=cmap, interpolation='nearest')
        plt.colorbar(label='Posterior Median')
        plt.title('Heatmap from Raster using Posterior Median')
        plt.show()
