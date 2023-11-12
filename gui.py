# Author: Joe Harrison
# Date: Nov 11, 2023
# License: MIT
# NOTE: DearPyGui is not officially supported on Windows 11

import dearpygui.dearpygui as dpg
import webbrowser

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QApplication

import capstone_roads  # our python file. Should be in the same working directory as this python script
import matplotlib.pyplot as plt
import geopandas as gpd

plt.switch_backend("Agg")  # so no issues with GUI backend
import seaborn as sns

sns.set_style("darkgrid", {"axes.facecolor": ".9"})
sns.set(rc={"figure.figsize": (8, 6)})


def main():
    dpg.create_context()

    def visualize(list_of_connected_dicts, shape_files, cols_list):
        gpd_files = gpd.GeoSeries(shape_files, crs=4326)  # passed in shape_files
        fig, ax = plt.subplots()
        gpd_files.plot(ax=ax, color=cols_list)

        plt.savefig(
            "road_clustering.png", bbox_inches="tight"
        )  # puts it in the working directory
        plt.close()

        width1, height1, channels, data2 = dpg.load_image("road_clustering.png")
        width2, height2, channels, data_loadings = dpg.load_image("pca_w_loadings.png")
        width3, height3, channels, data = dpg.load_image("road_pca.png")

        with dpg.texture_registry(show=False):
            dpg.add_static_texture(
                width=width1,
                height=height1,
                default_value=data2,
                tag="road_clustering",
            )
        with dpg.texture_registry(show=False):
            dpg.add_static_texture(
                width=width2,
                height=height2,
                default_value=data_loadings,
                tag="pca_w_loadings",
            )
        with dpg.texture_registry(show=False):
            dpg.add_static_texture(
                width=width3, height=height3, default_value=data, tag="road_pca"
            )

        with dpg.window(label="Clustering Results"):
            dpg.add_image("road_clustering")
            dpg.add_image("pca_w_loadings")
            dpg.add_image("road_pca")

    def run_script():
        filepath = dpg.get_value(fp)
        print("our filepath is", filepath)
        dpg.hide_item(run_button)
        dpg.show_item(slow_warning)

        # dpg.show_item(progress_bar)

        (
            start_time,
            data,
            tree,
            list_of_dicts,
            set_of_looked_at_roads,
            num_roads,
            shape_files,
        ) = capstone_roads.setup(filepath)

        # in the old formulation, this would give us the progress bar
        # for i in tqdm(range(size)):

        i = 0
        while True:
            try:
                i = i + 1
                val = next(
                    capstone_roads.create_data_for_road(
                        i, set_of_looked_at_roads, list_of_dicts, tree, data
                    )
                )
                dpg.set_value(
                    "viewer",
                    f"{val + 1} out of {num_roads} ({round(val*100/num_roads, 1)}%)",
                )
            except:
                dpg.hide_item(progress_bar)
                break

        list_of_connected_dicts, shape_files = capstone_roads.graph_analysis(
            list_of_dicts, start_time, shape_files
        )

        cols_list = capstone_roads.show_results(list_of_connected_dicts)
        dpg.hide_item(slow_warning)
        dpg.hide_item(text1)
        dpg.hide_item(button1)
        dpg.hide_item(button2)
        dpg.hide_item(text2)
        visualize(list_of_connected_dicts, shape_files, cols_list)

    def get_user_link():
        app = QApplication([])  # Create a QApplication instance if not already created
        directory = QFileDialog.getOpenFileName(
            None, "Select Directory", "", "Zip Files (*.zip);;SHP Files (*.shp)"
        )
        print(directory)
        dir = str(directory[0])
        dpg.set_value(fp, dir)
        dpg.show_item(run_button)

    def download():
        webbrowser.open_new(
            "https://www.census.gov/cgi-bin/geo/shapefiles/index.php?year=2022&layergroup=Roads"
        )

    def city_finder():
        webbrowser.open_new(
            "https://www.statsamerica.org/CityCountyFinder/Default.aspx"
        )

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameRounding, 6, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_FrameBorderSize, 2, category=dpg.mvThemeCat_Core
            )
            dpg.add_theme_style(
                dpg.mvStyleVar_ScrollbarSize, 4, category=dpg.mvThemeCat_Core
            )

    with dpg.window(label="Chose Road Network to Analyze", width=600, height=400):
        text1 = dpg.add_text("Select the City / County to download your roads from")
        button1 = dpg.add_button(label="Download Roads to Analyze", callback=download)
        button2 = dpg.add_button(
            label="If you don't find your city / town, click here to find the county (then download from above)",
            callback=city_finder,
        )
        text2 = dpg.add_text("...once files are downloaded")
        zip = dpg.add_button(
            label="Link to .zip Folder of Roads or .shp file", callback=get_user_link
        )
        dpg.add_text("")

        fp = dpg.add_text(label="file_path", default_value="no path defined yet")

        run_button = dpg.add_button(
            label="Run", callback=run_script, user_data=dpg.get_value(fp)
        )
        dpg.hide_item(run_button)  # only show once the user puts in the zip file

        progress_bar = dpg.add_progress_bar(label="progress")
        dpg.hide_item(progress_bar)

        slow_warning = dpg.add_loading_indicator()
        dpg.hide_item(slow_warning)

        viewer = dpg.add_text(label="Text", tag="viewer")
        # dpg.hide_item(viewer)

    dpg.bind_theme(global_theme)

    dpg.create_viewport(title="Analyze Roads", width=800, height=600)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
