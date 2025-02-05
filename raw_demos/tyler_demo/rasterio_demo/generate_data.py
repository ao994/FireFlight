import csv
import numpy as np

# function to generate clustered csv with varying density and spread out clusters
def generate_clustered_csv(output_file, num_points=10000, num_clusters=20, min_cluster_radius=0.01, max_cluster_radius=0.2, max_density=100):
    # define the bounds for latitude and longitude
    min_lat = 35.0  # minimum latitude
    max_lat = 36.0  # maximum latitude
    min_lon = -112.0  # minimum longitude
    max_lon = -111.0  # maximum longitude

    # generate cluster centers
    cluster_centers = []
    for _ in range(num_clusters):
        lat = np.random.uniform(min_lat + max_cluster_radius, max_lat - max_cluster_radius)
        lon = np.random.uniform(min_lon + max_cluster_radius, max_lon - max_cluster_radius)
        cluster_centers.append((lat, lon))

    # open the csv file for writing
    with open(output_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Latitude', 'Longitude', 'Density'])

        # generate points for each cluster
        for _ in range(num_points):
            # randomly pick a cluster center
            center = cluster_centers[np.random.randint(len(cluster_centers))]
            center_lat, center_lon = center

            # generate cluster radius using exponential distribution
            cluster_radius = np.random.exponential(scale=(max_cluster_radius - min_cluster_radius) / 2) + min_cluster_radius

            # generate a random spread for points around the cluster center
            lat = np.random.normal(loc=center_lat, scale=cluster_radius / 3)
            lon = np.random.normal(loc=center_lon, scale=cluster_radius / 3)

            # generate a density value that is higher for points closer to the cluster center
            distance = np.sqrt((lat - center_lat) ** 2 + (lon - center_lon) ** 2)

            if cluster_radius > 0.1:
                # large clusters will have a lower density around the edges
                density = max(0, int(max_density * np.exp(-distance ** 2 / (2 * cluster_radius ** 2))))
            else:
                # small clusters have higher density around the center
                density = max(0, int(max_density * np.exp(-distance ** 2 / (2 * (cluster_radius / 2) ** 2))))

            # write the generated point to the csv file
            writer.writerow([lat, lon, density])

    print(f"CSV file '{output_file}' created with clustered heatmap data.")

# call the function
if __name__ == "__main__":
    generate_clustered_csv('clustered_heatmap.csv', num_points=10000, num_clusters=30, min_cluster_radius=0.01, max_cluster_radius=0.2, max_density=100)