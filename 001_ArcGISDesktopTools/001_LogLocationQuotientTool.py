#-------------------------------------------------------------------------------
# Name:        LLQTool.py
# Purpose:     This script compares point density of two datasets in a known boundary
#              The script is written as an ArcGIS Python Tool and needs to be executed in python toolbox
#
# Author:      Xu Yuting 
#
# Created:     16/03/2021
# Copyright:   (c) ytxu 2021
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, os, sys
import datetime


class LicenseError(Exception):
    pass


class DataError(Exception):
    pass


class GeometryError(Exception):
    pass


def check_product_and_license():

    """
    This function validates that all necessary licenses are available
    :return: True/False
    """

    try:

        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")

        else:
            raise LicenseError

    except LicenseError:
        arcpy.AddMessage("Spatial Analyst license is unavailable. Terminate the process.")
        sys.exit()

    except arcpy.ExecuteError:
        arcpy.AddMessage(arcpy.GetMessages(2))


def get_inputs():

    """
    This function obtains input variables from user as parameters
    :return: variables received
    """

    feature_class_A = arcpy.GetParameterAsText(0)
    feature_class_B = arcpy.GetParameterAsText(1)
    study_area_polygon = arcpy.GetParameterAsText(2)
    radius = arcpy.GetParameterAsText(3)

    return feature_class_A, feature_class_B, study_area_polygon, radius


def project_to_PCS(in_feature_class):

    """
    Project a feature class from GCS to PCS
    :param in_feature_class: input feature class path
    :return: projected PCS feature layer path
    """

    # define output projected coordinate system
    out_coordinate_system = arcpy.SpatialReference('NAD 1983 HARN Contiguous USA Albers')
    out_feature_class = in_feature_class + "_projected"

    # run the tool to perform projection
    arcpy.Project_management(in_feature_class, out_feature_class, out_coordinate_system)

    return out_feature_class


def validate_inputs(feature_class_A, feature_class_B, study_area_polygon, radius):

    """
    This function validates and transforms the input variables received, and raises errors (if any).
    :return: validated/transformed input variables
    """

    # create a list container used in for loop
    feature_class_input = [feature_class_A, feature_class_B, study_area_polygon]
    feature_class_output = []

    for feature_class in feature_class_input:

        out_feature_class = feature_class
        feature_class_name = feature_class.split("\\")[-1]
        arcpy.AddMessage("\t\t| -- Checking layer {}...".format(feature_class_name))

        try:

            # check path validity and geometry type
            if not arcpy.Exists(feature_class):
                raise DataError

            desc = arcpy.Describe(feature_class)

            # for the first two feature classes, point geometry is expected
            if feature_class_input.index(feature_class) < 2:
                if desc.shapeType != 'Point':
                    raise GeometryError
            # for the last feature class, polygon geometry is expected
            else:
                if desc.shapeType != 'Polygon':
                    raise GeometryError

            # check the spatial reference of input feature class, convert to PCS as a new feature class if necessary
            if desc.spatialReference == "GCS_WGS_1984":
                arcpy.AddMessage("\t\t| -- {} is in GCS. Projecting to PCS...".format(feature_class_name))
                out_feature_class = project_to_PCS(feature_class)

        # if path is invalid, raise data error and terminate
        except DataError:
            arcpy.AddError("\t\t| -- Path to {} is not valid. Terminate the process.".format(feature_class_name))
            sys.exit()

        # if geometry type is incorrect, raise geometry error and terminate
        except GeometryError:
            arcpy.AddError("\t\t| -- Feature class {} is in an unexpected geometry. \
                            Terminate the process".format(feature_class_name))
            sys.exit()

        # if other error, display as a message
        except arcpy.ExecuteError:
            arcpy.AddMessage(arcpy.GetMessages(2))

        # append output feature class to a new list
        feature_class_output.append(out_feature_class)

    arcpy.AddMessage("\t\t| -- Checking radius...")
    # check if radius is an integer of float value, if not, convert to float
    if not isinstance(radius, (int, float)):
        arcpy.AddMessage("\t\t| -- Converting radius to numerical...")

        # try to convert to float; if failed, raise error and terminate
        try:
            radius = float(radius)
        except arcpy.ExecuteError:
            arcpy.AddError("\t\t| -- Unable to convert radius to numerical. Terminate the process")
            sys.exit()

    # return the new output feature class list and new radius value
    return feature_class_output, radius


def main():

    # Step 1. check product and extension license
    arcpy.AddMessage("0%    | Checking license and extension...")
    check_product_and_license()
    arcpy.env.overwriteOutput = True

    # Step 2. get input from user
    arcpy.AddMessage("5%    | Reading inputs...")
    dataset_A, dataset_B, study_area_polygon, radius = get_inputs()

    # Step 3. validate inputs
    arcpy.AddMessage("10%   | Validating inputs...")
    [dataset_A, dataset_B, study_area_polygon], radius = validate_inputs(dataset_A, dataset_B, study_area_polygon, radius)

    # Step 4a. calculate KDE
    arcpy.AddMessage("20%   | Calculating kernel density for feature class A...")
    kernel_density_A = arcpy.sa.KernelDensity(dataset_A, "NONE",
                                              search_radius=radius,
                                              area_unit_scale_factor="SQUARE_KILOMETERS",
                                              out_cell_values="DENSITIES",
                                              method="GEODESIC")

    arcpy.AddMessage("30%   | Calculating kernel density for feature class B...")
    kernel_density_B = arcpy.sa.KernelDensity(dataset_B, "NONE",
                                              search_radius=int(radius),
                                              area_unit_scale_factor="SQUARE_KILOMETERS",
                                              out_cell_values="DENSITIES",
                                              method="GEODESIC")

    # Step 4b. Clip KDE raster to study area
    arcpy.AddMessage("40%   | Clipping raster to study area...")
    clipped_kernel_density_A = os.path.join(arcpy.env.workspace, "KernelD_A_Clip")
    clipped_kernel_density_B = os.path.join(arcpy.env.workspace, "KernelD_B_Clip")

    arcpy.Clip_management(kernel_density_A,
                          "",
                          clipped_kernel_density_A,
                          in_template_dataset=study_area_polygon,
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")

    arcpy.Clip_management(kernel_density_B,
                          "",
                          clipped_kernel_density_B,
                          in_template_dataset=study_area_polygon,
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")


    # Step 5. calculate density ratio using z value of 0.000001
    arcpy.AddMessage("50%   | Calculating average density...")
    output_raster_avg = arcpy.sa.RasterCalculator([clipped_kernel_density_A, clipped_kernel_density_B],
                                                  ["x", "y"],
                                                  '(x + 0.000001)/(y + 0.000001)')

    # Calculate zonal statistics to get national mean value as denominator
    arcpy.AddMessage("60%   | Dissolving study area into single polygon...")
    dissolved_study_area = os.path.join(arcpy.env.workspace, "dissolved_polygon")
    arcpy.management.Dissolve(study_area_polygon, dissolved_study_area)

    arcpy.AddMessage("70%   | Calculating mean density in study area...")
    zonal_stats_output = arcpy.sa.ZonalStatistics(dissolved_study_area,
                                                  "OBJECTID",
                                                  output_raster_avg,
                                                  statistics_type="MEAN")

    # Step 6. Calculate LLQ and generate output raster
    arcpy.AddMessage("80%   | Calculating LLQ...")
    output_raster = arcpy.sa.RasterCalculator([clipped_kernel_density_A, clipped_kernel_density_B, zonal_stats_output],
                                              ["x", "y", "z"],
                                              'Log2((x+0.000001)/(y+0.000001)/z)')

    arcpy.AddMessage("90%   | Saving output to path...")
    output_raster_name = dataset_A.split("\\")[-1] + "_vs_" + dataset_B.split("\\")[-1]
    output_raster_path = os.path.join(arcpy.env.workspace, output_raster_name)

    # check if output raster name is used; if yes, rename the expected output raster
    if arcpy.Exists(output_raster_path):
        arcpy.AddMessage("      | -- Output file already exists. Renaming the file...")
        output_raster_name += "_{}".format(datetime.datetime.now().strftime("%Y%m%d_%H%M"))
        output_raster_path = os.path.join(arcpy.env.workspace, output_raster_name)

    # save output raster to disk
    output_raster.save(output_raster_path)

    # try to add output raster to active map in ArcGIS Pro
    try:
        arcpy.AddMessage("95%   | Displaying output in active map...")
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map_item = aprx.activeMap
        map_item.addDataFromPath(output_raster_path)

    # if unable to open active map, skip this step
    except arcpy.ExecuteError:

        pass

    finally:

        arcpy.AddMessage("100%  | Clearing workspace cache...")
        arcpy.ClearWorkspaceCache_management()
        arcpy.AddMessage("100%  | Completed")


if __name__ == '__main__':
    main()

