import os
import numpy as np
import folium
import rasterio
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from rasterio.transform import from_origin
from scipy.ndimage import gaussian_filter  # For smoothing
from map_app.models import Species, Grid, Results

class Command(BaseCommand):
    help = 'Generate a Folium map with a heatmap raster overlay created from Results model data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting heatmap raster generation and Folium map creation...'))

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

        # Generate the heatmap raster GeoTIFF.
        bounds = self.create_heatmap_raster(raster_tif)

        # Use the colorblind-friendly 'viridis' colormap without setting transparency.
        viridis_cmap = plt.get_cmap('viridis').copy()
        # (Removed: viridis_cmap.set_bad(color=(1, 1, 1, 1)))

        # Convert the GeoTIFF to PNG using the viridis colormap.
        bounds = self.convert_geotiff_to_png(raster_tif, raster_png, viridis_cmap)
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
        Queries Results for grid coordinates and posterior median values,
        builds a raster grid, applies smoothing and scaling,
        and writes a GeoTIFF.
        Returns the raster bounds.
        """
        latitudes, longitudes, medians = [], [], []
        results = Results.objects.select_related('bird_speciesID', 'gridID').all()
        for result in results:
            grid = result.gridID
            latitudes.append(grid.Grid_Lat_NAD83)
            longitudes.append(grid.Grid_Long_NAD83)
            medians.append(result.posterior_median)

        min_lat, max_lat = min(latitudes), max(latitudes)
        min_lon, max_lon = min(longitudes), max(longitudes)
        pixel_size = 0.01  # Adjust as needed.
        nrows = int((max_lat - min_lat) / pixel_size) + 1
        ncols = int((max_lon - min_lon) / pixel_size) + 1
        raster_data = np.zeros((nrows, ncols), dtype=np.float32)
        transform = from_origin(min_lon, max_lat, pixel_size, pixel_size)

        for lat, lon, median in zip(latitudes, longitudes, medians):
            row = int((max_lat - lat) / pixel_size)
            col = int((lon - min_lon) / pixel_size)
            raster_data[row, col] = median

        # Apply Gaussian smoothing (sigma=2.0) and boost intensity.
        raster_data = gaussian_filter(raster_data, sigma=2.0)
        raster_data = raster_data * 20

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
        Reads a GeoTIFF, normalizes its data with clipping for high intensities,
        and saves it as a PNG using the provided colormap.
        Returns the raster bounds.
        """
        with rasterio.open(geotiff_path) as src:
            data = src.read(1)
            bounds = src.bounds

        masked_data = np.ma.masked_equal(data, 0.0)
        if masked_data.max() - masked_data.min() > 0:
            norm_data = (masked_data - masked_data.min()) / (masked_data.max() - masked_data.min())
        else:
            norm_data = masked_data

        # Clip at the 95th percentile to saturate high values.
        thresh = np.percentile(norm_data.compressed(), 95)
        norm_data = np.clip(norm_data, 0, thresh)
        norm_data = norm_data / thresh

        plt.imsave(png_path, norm_data, cmap=cmap, vmin=0, vmax=1)
        return bounds
