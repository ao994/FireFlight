import os
import folium
import rasterio
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from matplotlib.colors import LinearSegmentedColormap

class Command(BaseCommand):
    help = 'Generate a Folium map of the Enchanted Circle region with the heatmap raster overlay.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting Folium map generation with raster overlay...'))

        # Define file paths for static images and templates
        static_dir = os.path.join('map_app', 'static', 'images')
        # Ensure the static images directory exists.
        if not os.path.exists(static_dir):
            os.makedirs(static_dir)
        raster_tif = os.path.join(static_dir, 'heatmap_raster.tif')
        raster_png = os.path.join(static_dir, 'heatmap_raster.png')
        
        # Define the templates directory path and ensure it exists.
        template_dir = os.path.join('map_app', 'templates')
        if not os.path.exists(template_dir):
            os.makedirs(template_dir)
        map_output = os.path.join(template_dir, 'enchanted_circle_map.html')

        # Define the custom colormap (should match the one used when generating the raster)
        green_yellow_red_cmap = LinearSegmentedColormap.from_list(
            'green_yellow_red', ['lightgreen', 'yellow', 'red'], N=256
        )

        # Convert the GeoTIFF raster to a PNG image and get its geographic bounds.
        bounds = self.convert_geotiff_to_png(raster_tif, raster_png, green_yellow_red_cmap)
        # Rasterio returns bounds as a named tuple (left, bottom, right, top)
        overlay_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]
        self.stdout.write(self.style.SUCCESS(f"Raster bounds: {overlay_bounds}"))

        # Create a Folium map centered on the Enchanted Circle region of New Mexico.
        # These coordinates ([36.5, -105.5]) are approximate; adjust if needed.
        m = folium.Map(location=[36.5, -105.5], zoom_start=9)

        # Add the raster overlay (PNG) to the Folium map.
        folium.raster_layers.ImageOverlay(
            image=raster_png,
            bounds=overlay_bounds,
            opacity=0.6,
            name='Heatmap Overlay',
            interactive=True,
            cross_origin=False,
            zindex=1,
        ).add_to(m)

        # Optionally add a layer control to the map.
        folium.LayerControl().add_to(m)

        # Save the resulting map as an HTML file in the templates folder.
        m.save(map_output)
        self.stdout.write(self.style.SUCCESS(f'Folium map generated and saved to: {map_output}'))

    def convert_geotiff_to_png(self, geotiff_path, png_path, cmap):
        """
        Reads a GeoTIFF file, extracts its data and geographic bounds,
        and saves the data as a PNG image using the provided colormap.
        Returns the raster bounds (a named tuple with left, bottom, right, top).
        """
        with rasterio.open(geotiff_path) as src:
            data = src.read(1)
            bounds = src.bounds  # bounds: left, bottom, right, top

        # Save the array as a PNG image using matplotlib with the provided colormap.
        plt.imsave(png_path, data, cmap=cmap)
        return bounds
