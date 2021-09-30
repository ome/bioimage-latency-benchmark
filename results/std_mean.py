import pandas

# Get the standard deviation and mean for all the benchmark data
# grouped by type (e.g. HDF5, TIFF, Zarr, Overhead) and by
# source (e.g. http, local, s3)

for csv_file in ["2d_benchmark_data.csv", "3d_benchmark_data.csv"]:

    print(csv_file)

    df = pandas.read_csv("2d_benchmark_data.csv")

    print("Mean")
    mean_values = df.groupby(["type", "source"]).mean()
    # or if you only want the "seconds" column
    # mean_values = mean_values["seconds"]
    print(mean_values)

    print("Std")
    std_values = df.groupby(["type", "source"]).std()
    print(std_values)
