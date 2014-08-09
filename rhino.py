import rhinoscriptsyntax as rs
obj=rs.GetObject("Select mesh",rs.filter.mesh)
print rs.MeshAreaCentroid(obj)