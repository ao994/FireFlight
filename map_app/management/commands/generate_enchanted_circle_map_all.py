import os
import numpy as np
import folium
import rasterio
import matplotlib.pyplot as plt
from django.conf import settings
from django.core.management.base import BaseCommand
from rasterio.transform import from_origin
from scipy.ndimage import gaussian_filter  # For smoothing
from matplotlib.colors import LinearSegmentedColormap
from map_app.models import Results

class Command(BaseCommand):
    help = ('Generate a Folium map with a heatmap raster overlay using a custom '
            'blue-white-orange colormap with a gradual gradient and interpolated data '
            'sourced directly from the database (Results).')

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting full DB heatmap raster generation and Folium map creation...'))

        # Ensure directories exist.
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

        # Generate the heatmap raster GeoTIFF from DB data.
        bounds = self.create_heatmap_raster(raster_tif)

        # Create a custom blue-white-orange colormap with a gradual gradient.
        custom_cmap = LinearSegmentedColormap.from_list(
            'custom_white_to_orange', 
            [
                (0.0, '#1f78b4'),   # Background blue (if needed)
                (0.3, '#1f78b4'),   # Maintain blue at low intensities
                (0.5, '#ffffff'),   # White (start of gradient)
                (0.65, '#ffe5cc'),  # Lighter orange
                (0.8, '#ffcc99'),   # Medium orange
                (1.0, '#ff7f00')    # Deep orange (center, highest intensity)
            ]
        )

        # Convert the GeoTIFF to PNG using the custom colormap.
        bounds = self.convert_geotiff_to_png(raster_tif, raster_png, custom_cmap)
        overlay_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
        self.stdout.write(self.style.SUCCESS(f"Raster bounds: {overlay_bounds}"))

        # Create a Folium map with the PNG overlay.
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
        m.save(map_output)
        self.stdout.write(self.style.SUCCESS(f'Folium map generated and saved to: {map_output}'))

    def create_heatmap_raster(self, output_raster):
        """
        Queries the Results table to obtain grid coordinates and posterior median values,
        builds a raster grid, applies Gaussian smoothing with a sigma value of 5 and intensity 
        scaling (multiplied by 20), writes a GeoTIFF, and returns the raster bounds.
        """
        latitudes, longitudes, medians = [], [], []
        results = Results.objects.select_related('gridID').all()
        for result in results:
            grid = result.gridID
            latitudes.append(grid.Grid_Lat_NAD83)
            longitudes.append(grid.Grid_Long_NAD83)
            medians.append(result.posterior_median)

        if not latitudes or not longitudes or not medians:
            self.stdout.write(self.style.ERROR("No valid data found in DB."))
            return

        # Define raster grid parameters.
        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lon, max_lon = min(longitudes), max(longitudes)
        pixel_size = 0.01  # Adjust as needed.
        nrows = int((max_lat - min_lat) / pixel_size) + 1
        ncols = int((max_lon - min_lon) / pixel_size) + 1
        raster_data = np.zeros((nrows, ncols), dtype=np.float32)
        transform = from_origin(min_lon, max_lat, pixel_size, pixel_size)
        
        # Populate the raster with the posterior median values.
        for lat, lon, median in zip(latitudes, longitudes, medians):
            row = int((max_lat - lat) / pixel_size)
            col = int((lon - min_lon) / pixel_size)
            if 0 <= row < nrows and 0 <= col < ncols:
                raster_data[row, col] = median

        # Apply Gaussian smoothing with sigma value 5 for interpolation.
        sigma_value = 5  # Interpolation parameter matching the CSV command.
        raster_data = gaussian_filter(raster_data, sigma=sigma_value)
        raster_data = raster_data * 20  # Boost intensity, as in the CSV version.

        # Write the smoothed/scaled raster to a GeoTIFF.
        with rasterio.open(
            output_raster, 'w', driver='GTiff',
            height=nrows, width=ncols, count=1, dtype='float32',
            crs='+proj=latlong', transform=transform
        ) as dst:
            dst.write(raster_data, 1)

        self.stdout.write(self.style.SUCCESS(f"Raster file created at '{output_raster}'."))
        with rasterio.open(output_raster) as src:
            return src.bounds

    def convert_geotiff_to_png(self, geotiff_path, png_path, cmap):
        """
        Reads the GeoTIFF, normalizes the data using percentile-based clipping (5th and 95th percentiles),
        saves as a PNG using the provided colormap, and returns the raster bounds.
        """
        with rasterio.open(geotiff_path) as src:
            data = src.read(1)
            bounds = src.bounds

        lower = np.percentile(data, 5)
        upper = np.percentile(data, 95)
        norm_data = np.clip(data, lower, upper)
        norm_data = (norm_data - lower) / (upper - lower)

        plt.imsave(png_path, norm_data, cmap=cmap, vmin=0, vmax=1)
        return bounds
