import copy
import math

class Point:
	def __init__(self, x, y):
		self.x=x
		self.y=y

	def __add__(self,other):
		x = self.x + other.x
		y = self.y + other.y
		return Point(x,y)

	def __sub__(self,other):
		x = self.x - other.x
		y = self.y - other.y
		return Point(x,y)

	def __mul__(self,factor):
		x = self.x * factor
		y = self.y * factor
		return Point(x,y)

	def __div__(self,factor):
		x = self.x / factor
		y = self.y / factor
		return Point(x,y)

	def __eq__(self, other):
		if (self.x==other.x and self.y==other.y) :
			return True
		else:
			return False

	def __ne__(self, other):
		if (self.x==other.x and self.y==other.y) :
			return False
		else:
			return True

	def __str__(self):
		return "Point(x=%s, y=%s)" % (self.x, self.y)

	def __hash__(self):
		return hash((self.x,self.y))
	__repr__=__str__


class Poly:
	def __init__(self):
		self.points=[]
		self.numpoints=0
		self.hole=False

	def Copy(self, src):
		self.points=copy.deepcopy(src.points)
		self.hole=src.hole
		self.numpoints=src.numpoints

	def Clear(self):
		self.points=[]
		self.numpoints=0
		self.hole=False

	def Init(self, numpoints):
		self.Clear()
		self.numpoints=numpoints
		self.points=[]

	def Triangle(self, p1, p2, p3):
		self.Init(3)
		self.Append(p1)
		self.Append(p2)
		self.Append(p3)
		return self

	def Square(self,p,side):
		self.Init(4)
		self.Append(p)
		self.Append(Point(p.x,p.y+side))
		self.Append(Point(p.x+side,p.y+side))
		self.Append(Point(p.x+side,p.y))
		return self

	def Append(self,p):
		self.points.append(p)
		self.numpoints=len(self.points)

	def Invert(self):
		self.points=self.points[::-1]

	def GetOrientation(self):
		area=0
		for i1 in range(self.numpoints):
			i2 = i1+1;
			if (i2 == self.numpoints):
				i2=0
			area += self.points[i1].x * self.points[i2].y - self.points[i1].y * self.points[i2].x 
		if area > 0 :
			return 1
		elif area < 0 :
			return -1
		else:
			return 0

	def GetArea(self):
		area=0
		for i1 in range(self.numpoints):
			i2 = i1+1;
			if (i2 == self.numpoints):
				i2=0
			area += self.points[i1].x * self.points[i2].y - self.points[i1].y * self.points[i2].x 
		return math.fabs(area/2.0)

	def SetOrientation(self,orientation):
		polyorientation = self.GetOrientation()
		if (polyorientation and polyorientation != orientation):
			self.Invert()

	def __eq__(self, other):
		if self.hole!=other.hole:
			return False
		if self.numpoints!=other.numpoints:
			return False
		for i in range(self.numpoints):
			if self.points[i]!=other.points[i]:
				return False
		return True
	def __str__(self):
		if self.hole :
			s="A hole "
		else:
			s="A non-hole "
		s+= "with %d points: {" % self.numpoints
		for p in self.points:
			s+= p.__str__()
		s+= "}"
		return s

	__repr__=__str__


class Partition:
	def __init__(self,max_length,min_detail):
		# """Init the partition with max_length and min_detail.
		# max_length: maximum allowed length of a side(in percentage)
		# """
		self.max_length=max_length
		self.min_detail=min_detail

	class PartitionVertex:
		def __init__(self, isActive, p):
			self.isActive=isActive
			self.isConvex=False
			self.isEar=False
			self.p=p
			self.angle=0
			self.previousv=None
			self.nextv=None
		def SetNeighbour(self, previousv, nextv):
			self.previousv=previousv
			self.nextv=nextv

	def IsConvex(self, p1, p2, p3):
		tmp = (p3.y-p1.y)*(p2.x-p1.x)-(p3.x-p1.x)*(p2.y-p1.y)
		# if tmp>0:
		# 	return True
		# # d1=self.Distance(p2,p1)
		# # d2=self.Distance(p3,p1)
		# # if d1>0 and d2>0:
		# # 	cos=((p3.x-p1.x)*(p2.x-p1.x)-(p3.y-p1.y)*(p2.y-p1.y))/math.sqrt(d1*d2)
		# # 	if cos<-0.9:
		# # 		return True
		# return False
		return tmp>0

	def IsReflex(self, p1, p2, p3):
		tmp = (p3.y-p1.y)*(p2.x-p1.x)-(p3.x-p1.x)*(p2.y-p1.y)
		return tmp<0
		# if tmp<=0:
		# 	return True
		# 	# d1=self.Distance(p2,p1)
		# 	# d2=self.Distance(p3,p1)
		# 	# if d1>0 and d2>0:
		# 	# 	cos=((p3.x-p1.x)*(p2.x-p1.x)-(p3.y-p1.y)*(p2.y-p1.y))/(d1*d2)
		# 	# 	if cos>-0.99:
		# 	# 		return True
		# return False
	def IsAcute(self,p1,p2,p3):
		if self.IsConvex(p1,p2,p3):
			cos=((p3.x-p1.x)*(p2.x-p1.x)+(p3.y-p1.y)*(p2.y-p1.y))/(self.Distance(p2,p1)*self.Distance(p3,p1))
			# print cos
			if cos>0.5:
				return True
		return False

	def InCone(self, p1, p2, p3, p):
		convex = self.IsConvex(p1,p2,p3)
		if convex:
			if not self.IsConvex(p1,p2,p):
				return False
			if not self.IsConvex(p2,p3,p):
				return False
			return True
		else:
			if self.IsConvex(p1,p2,p):
				return True
			if self.IsConvex(p2,p3,p):
				return True
			return False

	def Normalize(self, p):
		n = math.sqrt(p.x*p.x+p.y*p.y)
		if n!=0:
			r = p/n
		else:
			r = Point(0,0)
		return r

	def Intersects(self,p11,p12,p21,p22):
		"""check if two lines intersects"""
		if p11.x==p21.x and p11.y==p21.y :
			return 0
		if p11.x==p22.x and p11.y==p22.y :
			return 0
		if p12.x==p21.x and p12.y==p21.y :
			return 0
		if p12.x==p22.x and p12.y==p22.y :
			return 0
		v1ort=Point(p12.y-p11.y,p11.x-p12.x)
		v2ort=Point(p22.y-p21.y,p21.x-p22.x)
		
		v = p21-p11
		dot21 = v.x*v1ort.x + v.y*v1ort.y
		v = p22-p11
		dot22 = v.x*v1ort.x + v.y*v1ort.y
		v = p11-p21
		dot11 = v.x*v2ort.x + v.y*v2ort.y
		v = p12-p21
		dot12 = v.x*v2ort.x + v.y*v2ort.y

		if dot11*dot12>0:
			return 0
		if dot21*dot22>0:
			return 0
		return 1

	def Smooth(self, inpolys):
		outpolys=copy.deepcopy(inpolys)
		for poly in outpolys:
			i=0
			while i<poly.numpoints:
				i2=(i+poly.numpoints-1)%poly.numpoints
				i3=(i+1)%poly.numpoints
				if poly.points[i]==poly.points[i2] or poly.points[i3]==poly.points[i2] or poly.points[i3]==poly.points[i] :
					del poly.points[i]
					poly.numpoints-=1
					continue
				if ((self.Distance(poly.points[i],poly.points[i2])+self.Distance(poly.points[i],poly.points[i3])-self.Distance(poly.points[i3],poly.points[i2]))/self.Distance(poly.points[i3],poly.points[i2]))<0.03 :
					# print self.Distance(poly.points[i],poly.points[i2]), self.Distance(poly.points[i],poly.points[i3]), self.Distance(poly.points[i3],poly.points[i2])
					del poly.points[i]
					poly.numpoints-=1
					continue
				i+=1
			if poly.numpoints<=0:
				outpolys.remove(poly)
		return outpolys

	def RemoveHoles(self, inpolys):
		"""simple heuristic procedure for removing holes from a list of polygons
		works by creating a diagonal from the rightmost hole vertex to some visible vertex
		time complexity: O(h*(n^2)), h is the number of holes, n is the number of vertices
		space complexity: O(n)
		params:
			inpolys : a list of polygons that can contain holes
					  vertices of all non-hole polys have to be in counter-clockwise order
					  vertices of all hole polys have to be in clockwise order
		returns a list of polygons without holes on success, 0 on failure"""
		# check for trivial case (no holes)
		hasholes=False
		for poly in inpolys:
			if poly.hole:
				hasholes=True
				break
		if not hasholes:
			outpolys = copy.deepcopy(inpolys)
			return outpolys

		# non-trivial cases
		outpolys=copy.deepcopy(inpolys)
		while True:
			#find the hole point with the largest x
			hasholes=False
			holepointindex=None
			hole=None
			for poly in outpolys:
				if not poly.hole:
					continue
				if not hasholes:
					hasholes=True
					hole=poly
					holepointindex=0
					holepoint=poly.points[holepointindex]
				for i in range(poly.numpoints):
					if poly.points[i].x > holepoint.x:
						hole=poly
						holepointindex=i
						holepoint=poly.points[holepointindex]
			if not hasholes:
				break
			#find the closest visible vertex
			pointfound=False
			bestpointindex=None
			outer=None
			for poly in outpolys:
				if poly.hole:
					continue
				for i in range(poly.numpoints):
					if poly.points[i].x <= holepoint.x:
						continue
					if not self.InCone(poly.points[(i+poly.numpoints-1)%poly.numpoints],
						poly.points[i],
						poly.points[(i+1)%poly.numpoints],
						holepoint):
						continue
					if pointfound:
						v1 = self.Normalize(poly.points[i]-holepoint)
						v2 = self.Normalize(bestpoint-holepoint)
						if v2.x>v1.x:
							continue #keep the one that minimize the angle with (1,0)
					pointvisible=True
					j=0
					for poly2 in outpolys:
						if poly2.hole:
							continue
						for j in range(poly2.numpoints):
							if self.Intersects(holepoint, poly.points[i],
								poly2.points[j],poly2.points[(j+1)%poly2.numpoints]):
								pointvisible=False
								break
						if not pointvisible:
							break
					if pointvisible:
						pointfound=True
						bestpoint=poly.points[i]
						outer=poly
						bestpointindex=i
			if not pointfound:
				return 0
			newpoly=Poly()
			newpoly.Init(outer.numpoints+hole.numpoints+2)
			for i in range(bestpointindex+1):
				newpoly.Append(outer.points[i])
			for i in range(hole.numpoints+1):
				newpoly.Append(hole.points[(i+holepointindex)%hole.numpoints])
			for i in range(bestpointindex,outer.numpoints):
				newpoly.Append(outer.points[i])
			outpolys.remove(outer)
			outpolys.remove(hole)
			outpolys.append(newpoly)
		return outpolys

	def Distance(self,p1,p2):
		dx=p2.x-p1.x
		dy=p2.y-p1.y
		return math.sqrt(dx*dx+dy*dy)

	def IsInside(self,p1,p2,p3,p):
		if self.IsConvex(p1,p,p2) or self.IsConvex(p2,p,p3) or self.IsConvex(p3,p,p1):
			return False
		return True

	def UpdateVertex(self,v,vertices):
		v1=v.previousv
		v3=v.nextv
		v.isConvex=self.IsConvex(v1.p, v.p, v3.p)
		vec1=self.Normalize(v1.p-v.p)
		vec3=self.Normalize(v3.p-v.p)
		v.angle=vec1.x*vec3.x+vec1.y*vec3.y
		if v.isConvex:
			v.isEar=True
			for vertex in vertices:
				if vertex.p==v.p or vertex.p==v1.p or vertex.p==v3.p:
					continue
				if self.IsInside(v1.p,v.p,v3.p,vertex.p):
					v.isEar=False
					break
		else:
			v.isEar=False

	def AddPoints(self,polys):
		for poly in polys:
			n=poly.numpoints
			points=[]
			for i in range(n):
				p=poly.points[(i+1)%n]-poly.points[i]
				nj=int(math.floor(self.Distance(poly.points[i],poly.points[(i+1)%n])/self.max_length)+1)
				for j in range(nj):
					points.append(poly.points[i]+p*j/nj)
			poly.points=points
			poly.numpoints=len(points)
		return polys

	def Triangulate_EC(self, poly, triangles):
		"""triangulates a polygon by ear clipping
		time complexity O(n^2), n is the number of vertices
		space complexity: O(n)
		params:
		   poly : an input polygon to be triangulated
				  vertices have to be in counter-clockwise order
		   triangles : a list of triangles (result)
		returns 1 on success, 0 on failure"""
		if poly.numpoints<3 :
			return 0
		if poly.numpoints==3:
			triangles.append(poly)
			return 1
		n=poly.numpoints
		vertices=[]
		for i in range(n):
			vertices.append(self.PartitionVertex(True,poly.points[i]))
		for i in range(n):
			vertices[i].SetNeighbour(vertices[(i+n-1)%n],vertices[(i+1)%n])
		for vertex in vertices:
			self.UpdateVertex(vertex,vertices)
		for i in range(n-3):
			earfound=False
			ear=None
			#find the most extruded ear
			for vertex in vertices:
				if not vertex.isActive:
					continue
				if not vertex.isEar:
					continue
				if not earfound:
					earfound=True
					ear=vertex
				else:
					# if math.fabs(math.fabs(vertex.angle)-0.5)<math.fabs(math.fabs(ear.angle)-0.5):
					if vertex.angle>ear.angle:
						ear=vertex
			if not earfound:
				return 0
			triangle=Poly()
			triangle.Triangle(ear.previousv.p,ear.p,ear.nextv.p)
			triangles.append(triangle)
			ear.isActive=False
			ear.previousv.nextv=ear.nextv
			ear.nextv.previousv=ear.previousv
			if i==n-4:
				break
			self.UpdateVertex(ear.previousv,vertices)
			self.UpdateVertex(ear.nextv,vertices)
		for vertex in vertices:
			if vertex.isActive:
				triangle=Poly()
				triangle.Triangle(vertex.previousv.p,vertex.p,vertex.nextv.p)
				triangles.append(triangle)
		return 1

	def Triangulate_EC_list(self, inpolys):
		"""triangulates a list of polygons that may contain holes by ear clipping algorithm
		first calls RemoveHoles to get rid of the holes, and then Triangulate_EC for each resulting polygon
		time complexity: O(h*(n^2)), h is the number of holes, n is the number of vertices
		space complexity: O(n)
		params:
		   inpolys : a list of polygons to be triangulated (can contain holes)
					 vertices of all non-hole polys have to be in counter-clockwise order
					 vertices of all hole polys have to be in clockwise order
		returns a list of triangles on success, 0 on failure"""
		triangles=[]
		result=self.RemoveHoles(self.AddPoints(self.Smooth(inpolys)))
		if result ==0:
			return 0
		for poly in result:
			if not self.Triangulate_EC(poly,triangles):
				return 0
		return triangles

	def ConvexPartition_HM(self, poly, parts):
		"""partitions a polygon into convex polygons by using Hertel-Mehlhorn algorithm
		the algorithm gives at most four times the number of parts as the optimal algorithm
		however, in practice it works much better than that and often gives optimal partition
		uses triangulation obtained by ear clipping as intermediate result
		time complexity O(n^2), n is the number of vertices
		space complexity: O(n)
		params:
		  poly : an input polygon to be partitioned
				 vertices have to be in counter-clockwise order
		  parts : resulting list of convex polygons
		returns 1 on success, 0 on failure"""
		# return the polygon if it is already convex
		convex=True
		for i in range(poly.numpoints):
			i2=(i+poly.numpoints-1)%poly.numpoints
			i3=(i+1)%poly.numpoints
			if self.IsReflex(poly.points[i2],poly.points[i],poly.points[i3]):
				convex=False
				break
		if convex:
			parts=copy.deepcopy(poly)
			return 1
		#the polygon is not convex, triangulate first
		triangles=[]
		if not self.Triangulate_EC(poly,triangles):
			return 0
		i1=0
		while i1 < len(triangles):
			poly1=triangles[i1]
			i11=i12=i22=i21=-1
			while i11 < poly1.numpoints-1:
				i11+=1
				d1=poly1.points[i11]
				i12=(i11+1)%poly1.numpoints
				d2=poly1.points[i12]
				isdiagonal=False
				for i2 in range(i1,len(triangles)):
					if i1==i2:
						continue
					poly2=triangles[i2]
					for i21 in range(poly2.numpoints):
						if d2!=poly2.points[i21]:
							continue
						i22=(i21+1)%poly2.numpoints
						if d1!=poly2.points[i22]:
							continue
						isdiagonal=True
						#update adjacent list here
						break
					if isdiagonal:
						break
				if not isdiagonal:
					continue

				i13=(i11+poly1.numpoints-1)%poly1.numpoints
				d3=poly1.points[i13]
				i14=(i12+1)%poly1.numpoints
				d4=poly1.points[i14]
				i23=(i21+poly2.numpoints-1)%poly2.numpoints
				d5=poly2.points[i23]
				i24=(i22+1)%poly2.numpoints
				d6=poly2.points[i24]

				# if (not (self.IsAcute(d1,d2,d3) or self.IsAcute(d1,d2,d6) or self.IsAcute(d2,d1,d4) or self.IsAcute(d2,d1,d5))) and (self.IsReflex(d3,d1,d6) or self.IsReflex(d5,d2,d4)):
				if self.IsReflex(d3,d1,d6) or self.IsReflex(d5,d2,d4):
					continue

				# p2=poly1.points[i11]
				# i13=(i11+poly1.numpoints-1)%poly1.numpoints
				# p1=poly1.points[i13]
				# i23=(i22+1)%poly2.numpoints
				# p3=poly2.points[i23]
				# # dis1=self.Distance(p1,p2)
				# # dis2=self.Distance(p3,p2)
				# # dis=self.Distance(poly1.points[i11],poly1.points[i12])
				# # isnarrow=False
				# # isnarrow=poly1.GetArea()/(dis*dis)<0.05 or poly2.GetArea()/(dis*dis)<0.05
				# if self.IsReflex(p1,p2,p3):
				# 	continue
				# p2=poly1.points[i12]
				# i13=(i12+1)%poly1.numpoints
				# p3=poly1.points[i13]
				# i23=(i21+poly2.numpoints-1)%poly2.numpoints
				# p1=poly2.points[i23]
				# # dis3=self.Distance(p1,p2)
				# # dis4=self.Distance(p3,p2)
				# if self.IsReflex(p1,p2,p3):
				# 	continue
				# if not isnarrow and self.IsReflex(p1,p2,p3) and (dis3>self.min_detail or dis4>self.min_detail):
				newpoly=Poly()
				newpoly.Init(poly1.numpoints+poly2.numpoints-2)
				if i12<i11:
					l=poly1.points[i12:i11]
				else:
					l=poly1.points[i12:]+poly1.points[:i11]
				for p in l:
					newpoly.Append(p)
				if i22<i21:
					l=poly2.points[i22:i21]
				else:
					l=poly2.points[i22:]+poly2.points[:i21]
				for p in l:
					newpoly.Append(p)
				del triangles[i2]
				triangles[i1]=newpoly
				poly1=newpoly
				# i11=-1
				i1=0
				break
				continue
			i1+=1
		for triangle in triangles:

			parts.append(triangle)
		return 1

			
	def ConvexPartition_HM_list(self, inpolys):		
		"""partitions a list of polygons into convex parts by using Hertel-Mehlhorn algorithm
		the algorithm gives at most four times the number of parts as the optimal algorithm
		however, in practice it works much better than that and often gives optimal partition
		uses triangulation obtained by ear clipping as intermediate result
		time complexity O(n^2), n is the number of vertices
		space complexity: O(n)
		params:
		   inpolys : an input list of polygons to be partitioned
					 vertices of all non-hole polys have to be in counter-clockwise order
					 vertices of all hole polys have to be in clockwise order
		returns the resulting list of convex polygons on success, 0 on failure"""
		parts=[]
		result=self.RemoveHoles(self.AddPoints(self.Smooth(inpolys)))
		if result ==0:
			return 0
		for poly in result:
			if not self.ConvexPartition_HM(poly,parts):
				return 0
		return parts

def Draw(polys, name):
	builder=SVGBuilder()
	builder.SetPolygons(polys)
	builder.SaveToFile(name)

def SaveInfo(polys, filename):
	f = open(filename, 'w')
	for i in range(len(polys)):
		f.write("{0}\t{1}\n".format(i, polys[i].GetArea()))

# def GetXMax(polys):
# 	xmax=-1
# 	for poly in polys:
# 		for p in poly.points:
# 			if p.x>xmax:
# 				xmax=p.x
# 	return xmax

# def GetXMin(polys):
# 	xmin=-1
# 	for poly in polys:
# 		for p in poly.points:
# 			if p.x<xmin:
# 				xmin=p.x
# 	return xmin

# def GetYMax(polys):
# 	ymax=-1
# 	for poly in polys:
# 		for p in poly.points:
# 			if p.y>ymax:
# 				ymax=p.y
# 	return ymax

# def GetYMin(polys):
# 	ymin=-1
# 	for poly in polys:
# 		for p in poly.points:
# 			if p.y<ymin:
# 				ymin=p.y
# 	return ymin

# def MakeGrid(l,inteval):
# 	xmin=GetXMin(l)
# 	xmax=GetXMax(l)
# 	ymin=GetYMin(l)
# 	ymax=GetYMax(l)
# 	grids=[]
# 	for i in range(int((ymax-ymin)/inteval)+1):
# 		for j in range(int((xmax-xmin)/inteval)+1):
# 			grids.append(Poly().Square(Point(xmin+j*inteval,ymin+i*inteval),inteval))
# 	return grids


#===============================================================================
# SVGBuilder
#===============================================================================
class SVGBuilder(object):
	
	def HtmlColor(self, val):
		return "#{0:06x}".format(val & 0xFFFFFF)
	
	def AlphaClr(self, val):
		return "{0:.2f}".format(float(val >> 24)/255)

	class StyleInfo(object):
		def __init__(self):
			self.brushClr = 0
			self.penClr = 0
			self.penWidth = 0.8
			self.showCoords = False
	
	class StyleInfoPlus(StyleInfo):
		
		def __init__(self):   
			SVGBuilder.StyleInfo.__init__(self)   
			self.polygons = []
			self.textlines = []
		
	def __init__(self):        
		self.GlobalStyle = SVGBuilder.StyleInfo()
		self.PolyInfoList = []
		self.PathHeader = " <path d=\""
		self.PathFooter = "\"\n style=\"fill:{0}; fill-opacity:{1}; fill-rule:{2}; stroke:{3}; stroke-opacity:{4}; stroke-width:{5:.2f};\" filter=\"url(#Gamma)\"/>\n\n"
		self.Header = """<?xml version=\"1.0\" standalone=\"no\"?> 
<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.0//EN\" 
\"http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd\"> 
\n<svg width=\"{0}px\" height=\"{1}px\" viewBox=\"0 0 {0} {1}\" version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\">
  <defs>
	<filter id="Gamma">
	  <feComponentTransfer>
		<feFuncR type="gamma" amplitude="1" exponent="0.3" offset="0" />
		<feFuncG type="gamma" amplitude="1" exponent="0.3" offset="0" />
		<feFuncB type="gamma" amplitude="1" exponent="0.3" offset="0" />
	  </feComponentTransfer>
	</filter>
  </defs>\n\n"""
	
	def AddPolygon(self, poly, brushColor=0x60138013, penColor=0xFF003300):
		if poly is None or len(poly) == 0: return
		pi = self.StyleInfoPlus()
		pi.penWidth = self.GlobalStyle.penWidth
		pi.showCoords = self.GlobalStyle.showCoords
		pi.brushClr = brushColor
		pi.penClr = penColor        
		pi.polygons.append(poly)
		self.PolyInfoList.append(pi)
	
	def SetPolygons(self, polys, brushColor=0x60138013, penColor=0xFF003300):
		if polys is None or len(polys) == 0: return
		pi = self.StyleInfoPlus()
		pi.penWidth = self.GlobalStyle.penWidth
		pi.showCoords = self.GlobalStyle.showCoords
		pi.brushClr = brushColor
		pi.penClr = penColor        
		pi.polygons = polys
		self.PolyInfoList.append(pi)
	
	def SaveToFile(self, filename, invScale = 1, margin = 10):
		if len(self.PolyInfoList) == 0: return False
		if invScale == 0: invScale = 1.0
		if margin < 0: margin = 0
		pi = self.PolyInfoList[0]
		# get bounding rect ...
		left = right = pi.polygons[0].points[0].x
		top = bottom = pi.polygons[0].points[0].y
		for pi in self.PolyInfoList:
			for p in pi.polygons:
				for i in range(p.numpoints):
					if p.points[i].x < left: left = p.points[i].x
					if p.points[i].x > right: right = p.points[i].x
					if p.points[i].y < top: top = p.points[i].y
					if p.points[i].y > bottom: bottom = p.points[i].y
		left *= invScale
		top *= invScale
		right *= invScale
		bottom *= invScale
		offsetX = -left + margin      
		offsetY = -top + margin      
					
		f = open(filename, 'w')
		m2 = margin * 2
		f.write(self.Header.format(right - left + m2, bottom - top + m2))
		for pi in self.PolyInfoList:
			f.write(self.PathHeader)
			for p in pi.polygons:
				cnt = p.numpoints
				if cnt < 3: continue
				f.write(" M {0:.2f} {1:.2f}".format(p.points[0].x * invScale + offsetX, p.points[0].y * invScale + offsetY))
				for i in range(1,cnt):
					f.write(" L {0:.2f} {1:.2f}".format(p.points[i].x * invScale + offsetX, p.points[i].y * invScale + offsetY))
				f.write(" z")
			fillRule = "evenodd"
			f.write(self.PathFooter.format(self.HtmlColor(pi.brushClr), 
				self.AlphaClr(pi.brushClr), fillRule, 
				self.HtmlColor(pi.penClr), self.AlphaClr(pi.penClr),  pi.penWidth))
	
		f.write("</svg>\n")
		f.close()
		return True
