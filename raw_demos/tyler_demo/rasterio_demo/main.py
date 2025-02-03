import csv
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from rasterio.transform import from_origin
from rasterio.enums import Resampling
from matplotlib.colors import LinearSegmentedColormap

# function to create the raster from the CSV
def create_heatmap_raster(csv_file, output_raster):
    # read csv and extract coordinates and density values
    latitudes = []
    longitudes = []
    densities = []

    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            latitudes.append(float(row['Latitude']))
            longitudes.append(float(row['Longitude']))
            densities.append(int(row['Density']))

    # define raster grid and resolution
    min_lat = min(latitudes)
    max_lat = max(latitudes)
    min_lon = min(longitudes)
    max_lon = max(longitudes)

    # define raster grid resolution (the cell size, e.g., 0.01 degrees for high resolution)
    pixel_size = 0.01  # Smaller pixel size for much finer resolution

    # calculate number of rows and columns in the raster
    nrows = int((max_lat - min_lat) / pixel_size) + 1
    ncols = int((max_lon - min_lon) / pixel_size) + 1

    # initialize the raster grid with zeros
    raster_data = np.zeros((nrows, ncols), dtype=np.float32)

    # create a transform to map the coordinates to pixel positions
    transform = from_origin(max_lon, min_lat + pixel_size, pixel_size, pixel_size)

    # fill raster data based on the CSV values
    for lat, lon, density in zip(latitudes, longitudes, densities):
        row = int((max_lat - lat) / pixel_size)
        col = int((lon - min_lon) / pixel_size)
        raster_data[row, col] = density

    # write the raster data to a new GeoTIFF file
    with rasterio.open(output_raster, 'w', driver='GTiff', 
                       height=nrows, width=ncols, count=1, dtype='float32',
                       crs='+proj=latlong', transform=transform) as dst:
        dst.write(raster_data, 1)

    print(f"Raster file '{output_raster}' created.")

    # visualize the heatmap
    visualize_raster(output_raster)

# function to visualize the raster using matplotlib
def visualize_raster(raster_file):
    # read the raster data using rasterio
    with rasterio.open(raster_file) as src:
        data = src.read(1) # single band raster

    # define the custom colormap (pale green to yellow to red)
    green_yellow_red_cmap = LinearSegmentedColormap.from_list(
        'green_yellow_red', ['lightgreen', 'yellow', 'red'], N=256)

    # plot the raster data using matplotlib
    plt.figure(figsize=(10, 6))
    plt.imshow(data, cmap=green_yellow_red_cmap, interpolation='nearest')
    plt.colorbar(label='Density')
    plt.title('Heatmap from Raster')
    plt.show()

def main():
    #c reate raster from the generated CSV
    csv_file = 'clustered_heatmap.csv'  # generated CSV file
    output_raster = 'heatmap_raster.tif'  # output raster file name
    create_heatmap_raster(csv_file, output_raster)

if __name__ == '__main__':
    main()