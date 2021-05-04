#-------------------------------------------------------------------------------
# Name:        AppendLUToFishnet
# Purpose:     This script appends land use information to a new polygon layer; serves as input for machine learning
#
# Author:      ytxu
#
# Created:     26/10/2020
# Copyright:   (c) ytxu 2020
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, os, sys, datetime

# ------------- Obtain input parameters from users --------------- #
fishnetGridLyr = arcpy.GetParameterAsText(0)
LU_lyr = arcpy.GetParameterAsText(1)
outputDissolveName = arcpy.GetParameterAsText(2)
intermediaryFGDB = arcpy.GetParameterAsText(3)
outputIntersectName = arcpy.GetParameterAsText(4)
LUNameField = arcpy.GetParameterAsText(5)


def main():
    arcpy.AddMessage("Process Start: "+str(datetime.datetime.now()))

    arcpy.AddMessage("Dissolving LU layer...")
    outputDissolve = os.path.join(intermediaryFGDB,outputDissolveName)
    arcpy.Dissolve_management(LU_lyr, outputDissolve, LUNameField, None, "MULTI_PART", "DISSOLVE_LINES")

    arcpy.AddMessage("Intersecting LU layer with Fishnet layer...")
    outputIntersect = os.path.join(intermediaryFGDB,outputIntersectName)
    arcpy.Intersect_analysis([fishnetGridLyr,outputDissolve], outputIntersect, "ALL", None, "INPUT")

    # get the list of land uses in LU feature class
    arcpy.AddMessage("Getting list of land uses...")
    LUList = []
    with arcpy.da.SearchCursor(outputDissolve,[LUNameField]) as in_cursor:
        for row in in_cursor:
            print(row[0])
            LUList.append(row[0])
    del in_cursor
    arcpy.AddMessage("All Land Use Types: ")
    arcpy.AddMessage(LUList)


    # add float fields to fishnet grid layer
    arcpy.AddMessage("Adding new fields to fishnet layer...")
    for lu in LUList:
        arcpy.AddField_management(fishnetGridLyr,lu,"FLOAT")

    # checking field names
    arcpy.AddMessage("Getting new field names...")
    fldList = arcpy.ListFields(fishnetGridLyr)
    fldList = [f.name for f in fldList if f.name not in ["OID","ObjectID","Shape_Area","Shape_Length","Shape"]]

    # update all to 0
    arcpy.AddMessage("Setting LU fields to 0...")
    for lu in fldList:
        arcpy.CalculateField_management(fishnetGridLyr,lu,0,"PYTHON3")

    # create matching field name dictionaries
    lu_dict = {}
    count = 0
    for lu in LUList:
        lu_dict[lu]=fldList[count]
        count+=1

    # start appending LU to field
    arcpy.AddMessage("START appending land use to fields: "+str(datetime.datetime.now()))
    arcpy.AddMessage(datetime.datetime.now())

    with arcpy.da.SearchCursor(outputIntersect,["LandUseDesc","FID_SG_Fishnet"]) as in_cursor:
        for row in in_cursor:
            calFldCursor = arcpy.da.UpdateCursor(fishnetGridLyr,[lu_dict[row[0]]],"OID={}".format(row[1]))
            for cell in calFldCursor:
                cell[0]=1
                calFldCursor.updateRow(cell)
            del calFldCursor
    del in_cursor
    arcpy.AddMessage("END appending land use to fields: "+str(datetime.datetime.now()))



if __name__ == '__main__':
    main()
