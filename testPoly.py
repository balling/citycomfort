import TPPL
import rhinoscriptsyntax as rs
def ReadPoly(f):
	p=TPPL.Poly()
	n=int(f.readline())
	p.Init(n)
	p.hole=int(f.readline())>0
	for i in range(n):
		line=f.readline()
		vals=line.split()
		p.points.append(TPPL.Point(int(vals[0])/1000,int(vals[1])/1000))
	if((p.GetOrientation()==1) == p.hole):
		p.Invert()
	return p

def ReadPolyList(filename):
	f=open(filename,"r")
	l=[]
	for i in range(0,int(f.readline())):
		l.append(ReadPoly(f))
	return l

l=ReadPolyList("test2.txt")
#TPPL.Parition(max_length,min_detail)
pa=TPPL.Partition(25,1)
TPPL.Draw(l,'./test_original.svg')
# TPPL.Draw(TPPL.MakeGrid(l,5000),'./test_grid.svg')
TPPL.Draw(pa.RemoveHoles(l),'./test_hole.svg')
TPPL.Draw(pa.Smooth(l),'./test_smooth.svg')
TPPL.Draw(pa.Triangulate_EC_list(l),'./test_triangle.svg')
partition=pa.ConvexPartition_HM_list(l)
TPPL.Draw(partition,'./test_partition.svg')
TPPL.SaveInfo(partition,'./test_info.txt')
# f = open("zones.obj", 'w')
# i=0
# for res in partition:
#     f.write("o {0}\n".format(i))
#     for point in res.points:
#         f.write("v {0} {1} 0\n".format(point.x, point.y))
#     f.write("f")
#     for j in range(0,res.numpoints):
#         f.write(" {0}//".format(i+j+1))
#     f.write("\n")
#     # f.write("f {0}// {1}// {2}//\n".format(i+res.GetNumPoints()-2, i+res.GetNumPoints()-1,i+1))
#     # f.write("f {0}// {1}// {2}//\n".format(i+res.GetNumPoints()-1, i+1, i+2))
#     i=i+res.numpoints
# f.close()
for res in partition:
	l=[]
	for point in res.points:
		l.append((point.x,point.y,0))
	surface=rs.AddSrfPt(l)
