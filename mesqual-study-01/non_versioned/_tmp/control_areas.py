import os
import geopandas as gpd
import matplotlib.pyplot as plt


def get_regions_with_TSO():
    regions['TSO'] = 'TenneT'
    regions['TSO'] = regions[['bld', 'TSO']].apply(
        lambda x: 'TransnetBW' if (
                x['bld'] == 'Baden-Württemberg'
        ) else x['TSO'], axis=1)

    regions['TSO'] = regions[['name', 'TSO']].apply(
        lambda x: 'TransnetBW' if (
                x['name'] == 'Landkreis Konstanz' or
                x['name'] == 'Landkreis Ravensburg' or
                x['name'] == 'Alb-Donau-Kreis' or
                x['name'] == 'Ulm' or
                x['name'] == 'Landkreis Biberach' or
                x['name'] == 'Landkreis Reutlingen' or
                x['name'] == 'Landkreis Heidenheim' or
                x['name'] == 'Ostalbkreis' or
                x['name'] == 'Landkreis Schwäbisch Hall' or
                x['name'] == 'Bodenseekreis'
        ) else x['TSO'], axis=1)

    regions['TSO'] = regions[['bld', 'TSO']].apply(
        lambda x: '50Hertz' if (
                x['bld'] == 'Berlin' or
                x['bld'] == 'Brandenburg' or
                x['bld'] == 'Mecklenburg-Vorpommern' or
                x['bld'] == 'Hamburg' or
                x['bld'] == 'Sachsen-Anhalt' or
                x['bld'] == 'Thüringen' or
                x['bld'] == 'Sachsen'
        ) else x['TSO'], axis=1)

    regions['TSO'] = regions[['bld', 'TSO']].apply(
        lambda x: 'amprion' if (
                x['bld'] == 'Rheinland-Pfalz' or
                x['bld'] == 'Saarland' or
                x['bld'] == 'Nordrhein-Westfalen'
        ) else x['TSO'], axis=1)

    regions['TSO'] = regions[['name', 'TSO']].apply(
        lambda x: 'amprion' if (
                x['name'] == 'Landkreis Donau-Ries' or
                x['name'] == 'Landkreis Dillingen an der Donau' or
                x['name'] == 'Landkreis Aichach-Friedberg' or
                x['name'] == 'Augsburg' or
                x['name'] == 'Landkreis Günzburg' or
                x['name'] == 'Landkreis Neu-Ulm' or
                x['name'] == 'Landkreis Unterallgeu' or
                x['name'] == 'Memmingen' or
                x['name'] == 'Kaufbeuren' or
                x['name'] == 'Landkreis Ostallgäu' or
                x['name'] == 'Landkreis Oberallgru' or
                x['name'] == 'Landkreis Lindau' or
                x['name'] == 'Kempten (Allgpu)' or
                x['name'] == 'Hochtaunuskreis' or
                x['name'] == 'Rheingau-Taunus-Kreis' or
                x['name'] == 'Main-Taunus-Kreis' or
                x['name'] == 'Wiesbaden' or
                x['name'] == 'Frankfurt am Main' or
                x['name'] == 'Landkreis Offenbach' or
                x['name'] == 'Offenbach am Main' or
                x['name'] == 'Kreis Grok-Gerau' or
                x['name'] == 'Darmstadt' or
                x['name'] == 'Landkreis Darmstadt-Dieburg' or
                x['name'] == 'Odenwaldkreis' or
                x['name'] == 'Landkreis Augsburg' or
                x['name'] == 'Kreis Bergstrare'
        ) else x['TSO'], axis=1)

    regions['TSO'] = regions[['name', 'TSO']].apply(
        lambda x: 'TenneT' if (
                x['name'] == 'Kreis Lippe' or
                x['name'] == 'Kreis Minden-Lübbecke' or
                x['name'] == 'Kreis Höxter' or
                x['name'] == 'Landkreis Diepholz' or
                x['name'] == 'Landkreis Nienburg/Weser' or
                x['name'] == 'Landkreis Schaumburg' or
                x['name'] == 'Landkreis Hameln-Pyrmont' or
                x['name'] == 'Landkreis Holzminden' or
                x['name'] == 'Landkreis Emsland' or
                x['name'] == 'Landkreis Osnabrück' or
                x['name'] == 'Osnabrück' or
                x['name'] == 'Landkreis Grafschaft Bentheim' or
                x['name'] == 'Kreis Höxter'
        ) else x['TSO'], axis=1)

    return regions


if __name__ == "__main__":

    regionfile = "DEU_ADM2.shp/DEU_ADM2.shp"
    regionfile = "/Users/helgeesch/Downloads/7530196/GER_NUTS3_TSOs.shp"
    if os.path.isfile(regionfile):
        regions = gpd.read_file(regionfile)
        regions["bld"] = 0
    else:
        raise NameError(
            f"File {regionfile} does not exist. Please download it from "
            "https://www.geoboundaries.org/data/1_3_3/zip/shapefile/DEU/DEU_ADM2.shp.zip "
            "and un-zip in this folder."
        )

    bldrfile = "vg2500_12-31.gk3.shape/vg2500/VG2500_LAN.shp"
    bldrfile = "/Users/helgeesch/Downloads/vg2500_12-31.gk3.shape/vg2500/VG2500_LAN.shp"
    if os.path.isfile(bldrfile):
        bldr = bldrfile  # "../data/vg2500_bld.shp"
        bldr = gpd.read_file(bldr).to_crs(epsg=4326)
    else:
        raise NameError(
            f"File {bldrfile} does not exist. Please download it from "
            "https://daten.gdz.bkg.bund.de/produkte/vg/vg2500/aktuell/vg2500_12-31.gk3.shape.zip "
            "and un-zip in this folder."
        )

    # mapping of regions to federal state
    for region_i in range(len(regions)):
        region = regions.iloc[region_i].geometry
        for bld_i in range(len(bldr)):
            bld = bldr.iloc[bld_i].geometry
            if bld.contains(region):
                regions.at[region_i, "bld"] = bldr.iloc[bld_i].GEN
            elif 100 * region.intersection(bld).area / region.area > 10:
                regions.at[region_i, "bld"] = bldr.iloc[bld_i].GEN
    regions.at[401, "bld"] = "Berlin"
    regions.at[402, "bld"] = "Hamburg"

    regions = get_regions_with_TSO()

    regions = (
        regions.rename(
            columns={"TSO": "tso"}
        )
        # .drop(columns=["Level", "adm", "adm_int"])
        .set_index("feature_id")
    )

    regions.to_file("GER_NUTS3_TSOs.shp")

    fig, ax = plt.subplots(figsize=(25, 25))
    regions.boundary.plot(ax=ax, color="black")
    regions[['geometry', 'tso']].plot(
        column='tso',
        legend=True,
        legend_kwds={'fontsize': 16},
        alpha=.3,
        ax=ax
    )
    ax.tick_params("both", labelsize=16)

    ax.set_title(
        "Control Zones of German Transmission System Operators", fontsize=24
    )

    plt.savefig("_tmp/GER_NUTS3_TSOs.png", bbox_inches='tight')
