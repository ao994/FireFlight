import os
import numpy as np
import folium
import rasterio
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from rasterio.transform import from_origin
from map_app.models import Species, Grid, Results

class Command(BaseCommand):
    help = 'Generate a Folium map with a heatmap raster overlay created from Results model data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting heatmap raster generation and Folium map creation...'))

        # Define directories for static images and templates.
        static_dir = os.path.join('map_app', 'static', 'images')
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        template_dir = os.path.join('map_app', 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        
        # Define file paths.
        raster_tif = os.path.join(static_dir, 'heatmap_raster.tif')
        raster_png = os.path.join(static_dir, 'heatmap_raster.png')
        map_output = os.path.join(template_dir, 'enchanted_circle_map.html')

        # Generate the heatmap raster GeoTIFF from model data.
        bounds = self.create_heatmap_raster(raster_tif)

        # Define the viridis colormap, a popular colorblind-friendly option.
        viridis_cmap = plt.get_cmap('viridis').copy()
        # Instead of transparent, set masked (no-data) values to white for better contrast.
        viridis_cmap.set_bad(color=(1, 1, 1, 1))  

        # Convert the GeoTIFF to a PNG image using the viridis colormap.
        bounds = self.convert_geotiff_to_png(raster_tif, raster_png, viridis_cmap)
        # Rasterio returns bounds as (left, bottom, right, top) so we form overlay bounds accordingly.
        overlay_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
        self.stdout.write(self.style.SUCCESS(f"Raster bounds: {overlay_bounds}"))

        # Create a Folium map centered on the Enchanted Circle region (approximate coordinates).
        m = folium.Map(location=[36.5, -105.5], zoom_start=9)
        folium.raster_layers.ImageOverlay(
            image=raster_png,
            bounds=overlay_bounds,
            opacity=0.6,
            name='Heatmap Overlay',
            interactive=True,
            cross_origin=False,
            zindex=1,
        ).add_to(m)
        folium.LayerControl().add_to(m)

        # Save the map as an HTML file.
        m.save(map_output)
        self.stdout.write(self.style.SUCCESS(f'Folium map generated and saved to: {map_output}'))

    def create_heatmap_raster(self, output_raster):
        """
        Queries the Results model for grid coordinates and posterior median values,
        builds a raster grid, and writes the data to a GeoTIFF file.
        Returns the raster bounds.
        """
        # Gather data from the Results model.
        latitudes = []
        longitudes = []
        medians = []
        results = Results.objects.select_related('bird_speciesID', 'gridID').all()

        for result in results:
            grid = result.gridID
            latitudes.append(grid.Grid_Lat_NAD83)
            longitudes.append(grid.Grid_Long_NAD83)
            medians.append(result.posterior_median)

        # Define the raster grid parameters.
        min_lat = min(latitudes)
        max_lat = max(latitudes)
        min_lon = min(longitudes)
        max_lon = max(longitudes)
        pixel_size = 0.01  # Adjust pixel size as needed.

        nrows = int((max_lat - min_lat) / pixel_size) + 1
        ncols = int((max_lon - min_lon) / pixel_size) + 1

        # Initialize the raster data array.
        raster_data = np.zeros((nrows, ncols), dtype=np.float32)

        # Define the geospatial transform.
        # from_origin expects (west, north, pixel_width, pixel_height).
        transform = from_origin(min_lon, max_lat, pixel_size, pixel_size)

        # Populate the raster array with posterior median values.
        for lat, lon, median in zip(latitudes, longitudes, medians):
            row = int((max_lat - lat) / pixel_size)
            col = int((lon - min_lon) / pixel_size)
            raster_data[row, col] = median

        # Write the raster data to a GeoTIFF file.
        with rasterio.open(
            output_raster, 'w', driver='GTiff', 
            height=nrows, width=ncols, count=1, dtype='float32',
            crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(raster_data, 1)

        self.stdout.write(self.style.SUCCESS(f"Raster file created at '{output_raster}'."))

        # Open the file again to retrieve its bounds.
        with rasterio.open(output_raster) as src:
            return src.bounds

    def convert_geotiff_to_png(self, geotiff_path, png_path, cmap):
        """
        Reads a GeoTIFF file, extracts its data and geographic bounds,
        and saves the data as a PNG image using the provided colormap.
        Returns the raster bounds.
        """
        with rasterio.open(geotiff_path) as src:
            data = src.read(1)
            bounds = src.bounds  # (left, bottom, right, top)

        # Mask data where values are 0.0 so they display with the specified background.
        masked_data = np.ma.masked_equal(data, 0.0)

        # Save the raster data as a PNG image using the provided colormap.
        plt.imsave(png_path, masked_data, cmap=cmap)
        return bounds
