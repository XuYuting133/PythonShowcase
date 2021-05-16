# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%
import os
import pandas as pd
import arcpy
folder = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\Processed\202101\Node\Bus"

node_attr_files = [f for f in os.listdir(folder) if "NodeAttributes" in f and ".csv" in f]


# %%
print(len(node_attr_files))
for f in node_attr_files:
    print(f)


# %%
fgdb = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\NodeAttributes_202101.gdb"
print("Importing excel to tables...")
arcpy.env.workspace = fgdb
arcpy.env.overwriteOutput = True

for f in node_attr_files:
    print(f)
    in_csv = os.path.join(folder, f)
    out_excel = os.path.join(folder, f.replace(".csv",".xlsx"))
    read_file = pd.read_csv(in_csv)
    if os.path.exists(out_excel):
        os.remove(out_excel)
    read_file.to_excel(out_excel, index = None, header=True)
    
    out_table = os.path.join(fgdb, f.replace(".csv",""))
    arcpy.ExcelToTable_conversion(out_excel, out_table, "Sheet1")


# %%
# Join Node Attributes to Bus Stop and Export as Feature Class
print("Creating joined feature classes...")
arcpy.env.workspace = fgdb
node_attr_tables = arcpy.ListTables()
arcpy.env.overwriteOutput = True
arcpy.env.qualifiedFieldNames = False

bus_stop = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\GE6211SDH.gdb\BusStop"
if arcpy.Exists("bus_stop_lyr"):
    arcpy.Delete_management("bus_stop_lyr")
arcpy.MakeFeatureLayer_management(bus_stop, "bus_stop_lyr")

for t in node_attr_tables:
    print(t)
    table = os.path.join(fgdb, t)
    
    day_type = t.split("_")[-2]
    day_hour = t.split("_")[-1]
    
    out_table_name = "BusStop_NodeAttr_{}_{}".format(day_type, day_hour)
    out_table = os.path.join(fgdb, out_table_name)
    
    # amend the bus_stop ID field
    if arcpy.Exists("table_view"):
        arcpy.Delete_management("table_view")
    arcpy.MakeTableView_management(table, "table_view")
    arcpy.CalculateField_management ("table_view", "BUS_STOP_N", "str(!Id!).zfill(5)", "PYTHON")
    arcpy.Delete_management("table_view")
    
    # Join the feature layer to a table
    veg_joined_table = arcpy.AddJoin_management("bus_stop_lyr", "BUS_STOP_N", table, 
                                            "BUS_STOP_N")
    
    
    
    # Copy the layer to a new permanent feature class
    arcpy.CopyFeatures_management("bus_stop_lyr", out_table)
    
    # Remove the join
    arcpy.RemoveJoin_management("bus_stop_lyr")
    


# %%
# check fields
fc_list = [f for f in arcpy.ListFeatureClasses() if "BusStop_NodeAttr_" in f]
print("Checking if necessary fields are in the feature class...")
required_fields = ["indegree","outdegree","Degree","weighted_indegree","weighted_outdegree","Weighted_Degree",
                      "Authority","Hub","modularity_class","pageranks","Eccentricity","closnesscentrality",
                       "harmonicclosnesscentrality","eigencentrality","clustering"]

for fc in fc_list:
    fc_path = os.path.join(fgdb, fc)
    
    field_names = [f.name for f in arcpy.ListFields(fc_path)]
    
    
    
    missing_fields = [f for f in required_fields if f not in field_names]
    
    print("{} is missing: ".format(fc) + repr(missing_fields))


# %%
# fill required fields with 0 if found NULL

fc_list = [f for f in arcpy.ListFeatureClasses() if "BusStop_NodeAttr_" in f]
print("Checking if necessary fields are in the feature class...")
required_fields = ["indegree","outdegree","Degree","weighted_indegree","weighted_outdegree","Weighted_Degree",
                      "Authority","Hub","modularity_class","pageranks","Eccentricity","closnesscentrality",
                       "harmonicclosnesscentrality","eigencentrality","clustering"]
field_count = len(required_fields)-1

for fc in fc_list:
    print(fc)
    fc_path = os.path.join(fgdb, fc)
    
    with arcpy.da.UpdateCursor(fc_path, required_fields) as in_cursor:
        for row in in_cursor:
            field_id = 0
            while field_id <= field_count:
                if row[field_id] is None:
                    row[field_id] = 0
                field_id += 1
            in_cursor.updateRow(row)
        
            


# %%
# create kernel density surface
print("Creating pageranks kernel density surface...")
arcpy.env.workspace = fgdb

fc_list = [f for f in arcpy.ListFeatureClasses() if "BusStop_NodeAttr_" in f]
out_gdb = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\PageRankSurface_202101.gdb"
default_gdb = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\GE6211SDH.gdb"

island = os.path.join(default_gdb, "MP14_Island")
arcpy.env.workspace = out_gdb
arcpy.env.overwriteOutput = True

for fc in fc_list:
    print(fc)
    
    
    fc_path = os.path.join(fgdb, fc)
    day_type = fc.split("_")[-2]
    day_hour = fc.split("_")[-1]
    
    postfix = "_".join([day_type, day_hour])
    out_kernel_name = "PolygonPRKernel_{}".format(postfix)
    out_kernel_path = os.path.join(out_gdb, out_kernel_name)
    
    # geenrate KD and clip to island
    print("Generating KD...")
    outKernelDensity = arcpy.sa.KernelDensity(fc_path, "pageranks", area_unit_scale_factor="SQUARE_KILOMETERS", 
                                              out_cell_values="DENSITIES", 
                                              method="PLANAR")
    outKernelDensity_clipped = os.path.join(out_gdb, "KD_PR_Clip_{}".format(postfix))
    
    print("Clipping...")
    arcpy.Clip_management(outKernelDensity,
                          "",
                          outKernelDensity_clipped,
                          in_template_dataset=island,
                          clipping_geometry="ClippingGeometry",
                          maintain_clipping_extent="NO_MAINTAIN_EXTENT")
    print(outKernelDensity_clipped)
    
    # unit-based normalization
    print("Generating Min...")
    min_raster_output = arcpy.sa.ZonalStatistics(island,
                                                  "OBJECTID",
                                                  outKernelDensity_clipped,
                                                  statistics_type="Minimum")
    
    print("Generatng Max...")
    max_raster_output = arcpy.sa.ZonalStatistics(island,
                                                  "OBJECTID",
                                                  outKernelDensity_clipped,
                                                  statistics_type="Maximum")
    
    print("Normalizing...")
    normalized_KD = arcpy.sa.RasterCalculator([outKernelDensity_clipped, min_raster_output, max_raster_output], 
                                              ["kd", "kmin", "kmax"],
                                              "(kd-kmin)/(kmax-kmin)")
    
    # save output    
    normalized_KD.save(out_kernel_name)
    
    # delete intermediate results
    arcpy.Delete_management(min_raster_output)
    arcpy.Delete_management(max_raster_output)
    arcpy.Delete_management(outKernelDensity)
    arcpy.Delete_management(outKernelDensity)
    arcpy.Delete_management(outKernelDensity)
    
    print(out_kernel_name)
    


# %%



# %%
# need spatial autocorrelation on the PR values - use as tessellation cell size and kernel density cell size
# spatial autocorrelation - distance of 1500m used

# for each busstopPR
print("Creating pageranks kernel density polygon...") 
arcpy.env.workspace = fgdb
fc_list = [f for f in arcpy.ListFeatureClasses() if "BusStop_NodeAttr_" in f] 
out_gdb = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\PageRankSurface_202101.gdb" 
default_gdb = r"C:\Users\ytxu\Documents\ArcGIS\Projects\GE6211SDH\GE6211SDH.gdb"
island = os.path.join(default_gdb, "MP14_Island") 
arcpy.env.workspace = out_gdb 
arcpy.env.overwriteOutput = True
tessel = os.path.join(default_gdb, "BlankTesselation_1500")

for fc in fc_list: 
    print(fc)
    
    fc_path = os.path.join(fgdb, fc)
    
    day_type = fc.split("_")[-2]
    day_hour = fc.split("_")[-1]
    
    postfix = "_".join([day_type, day_hour])
    
    # Process: Kernel Density (Kernel Density) (sa)
    print("Generating PR kernel density...")
    pagerank_kd_name = "pr_kd_nafilled_{}".format(postfix)
    pagerank_kd = os.path.join(out_gdb, pagerank_kd_name)
    
    pr_kd_output = arcpy.sa.KernelDensity(in_features=fc_path, 
                                          population_field="pageranks", 
                                          search_radius=750, 
                                          area_unit_scale_factor="SQUARE_KILOMETERS", 
                                          out_cell_values="DENSITIES", 
                                          method="PLANAR")
    # pr_kd_output.save(pagerank_kd)
    
    # fill null value with 0
    print("Filling null...")
    pr_kd_fillna = arcpy.sa.RasterCalculator([pr_kd_output], 
                                              ["x"],
                                              "Con(IsNull(x),0,x)")
    pr_kd_fillna.save(pagerank_kd)
    
    # calculate min and max
    print("Generating Min...")
    min_raster_output = arcpy.sa.ZonalStatistics(island,
                                                  "OBJECTID",
                                                  pr_kd_fillna,
                                                  statistics_type="Minimum")
    
    print("Generatng Max...")
    max_raster_output = arcpy.sa.ZonalStatistics(island,
                                                  "OBJECTID",
                                                  pr_kd_fillna,
                                                  statistics_type="Maximum")
    
    print("Normalizing...")
    normalized_KD = arcpy.sa.RasterCalculator([pr_kd_fillna, min_raster_output, max_raster_output], 
                                              ["kd", "kmin", "kmax"],
                                              "(kd-kmin)/(kmax-kmin)")
    
    
    # Process: Zonal Statistics - Get mean within each tessellation cell
    print("Calculating zonal mean...")
    tessel_mean = arcpy.sa.ZonalStatistics(in_zone_data=tessel, 
                                           zone_field="OBJECTID", 
                                           in_value_raster=normalized_KD, 
                                           statistics_type="MEAN", 
                                           ignore_nodata="DATA", 
                                           process_as_multidimensional="CURRENT_SLICE", 
                                           percentile_value=90, 
                                           percentile_interpolation_type="AUTO_DETECT")    
    # Converting to integer
    print("Converting to integer...")
    int_tessel_mean = arcpy.sa.RasterCalculator([tessel_mean], 
                                              ["x"],
                                              "Int(5000*x)")
    
    # Raster to polygon
    print("Converting raster to polygon...")
    tessel_polygon = os.path.join(out_gdb, "PolygonTesselMean_{}".format(postfix))
    arcpy.conversion.RasterToPolygon(in_raster=int_tessel_mean, 
                                     out_polygon_features=tessel_polygon, 
                                     simplify="SIMPLIFY", 
                                     raster_field="Value", 
                                     create_multipart_features="SINGLE_OUTER_PART", 
                                     max_vertices_per_feature=None)
    
    print(tessel_polygon)
    
    arcpy.Delete_management(int_tessel_mean)
    arcpy.Delete_management(tessel_mean)
    arcpy.Delete_management(normalized_KD)
    arcpy.Delete_management(min_raster_output)
    arcpy.Delete_management(max_raster_output)
    arcpy.Delete_management(min_raster_output)
    arcpy.Delete_management(pr_kd_output)
    


# %%



# %%



