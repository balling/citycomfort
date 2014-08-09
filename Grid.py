import copy
import math
import TPPL
import random

# def ReadPoly(f):
# 	p=TPPL.Poly()
# 	n=int(f.readline())
# 	p.Init(n)
# 	p.hole=int(f.readline())>0
# 	for i in range(n):
# 		line=f.readline()
# 		vals=line.split()
# 		p.points.append(TPPL.Point(int(vals[0]),int(vals[1])))
# 	if((p.GetOrientation()==1) == p.hole):
# 		p.Invert()
# 	return p

# def ReadPolyList(filename):
# 	f=open(filename,"r")
# 	l=[]
# 	for i in range(0,int(f.readline())):
# 		l.append(ReadPoly(f))
# 	pa=TPPL.Partition(25000,50)
# 	p=pa.RemoveHoles(pa.Smooth(l))
# 	return p

class GridCell:
	def __init__(self,shape=None,normal=1,val=None,active=False):
		self.shape=shape
		self.val=val
		self.normal=normal
		self.active=active

class SVFGrid:
	def __init__(self,n,thres,side,ratio,svfFilename="building1407svf1.txt"):
		self.grids=[]
		self.n=n
		self.activecnt=0
		self.interval=10
		self.svfs=[]
		self.newsvf=[]
		self.side=side*n
		self.ratio=ratio
		f=open(svfFilename,"r")	
		for i in range(n):
			line=f.readline()
			vals=line.split()
			self.svfs+=map(float,vals)
		zone=[]
		for i in range(self.n*self.n):
			grid=GridCell(TPPL.Poly().Square(TPPL.Point((i/self.n)*self.interval,(i%self.n)*self.interval),self.interval))
			self.grids.append(grid)
			if self.svfs[i]==0:
				grid.val=-1
			else:
				grid.val=-2
				zone.append(i)
		zones=self.Compute(zone,thres)
		self.Draw(zones)
		newzones=self.LoadNewSVF(zones)
		self.Draw(newzones,"newzones.svg")
		self.ToOBJ(zones)
		self.ToOBJ(newzones,900,"newzones.obj")
		self.SaveInfo(2,zonelists=[zones,newzones],heights=[900,900])
		# print self.vals
		# Draw(self.grids,"grid.svg")

	def LoadNewSVF(self,zones):
		self.newsvf=[]
		newzones=copy.deepcopy(zones)
		f=open("building1407svf_new.txt","r")
		for i in range(self.n):
			line=f.readline()
			vals=line.split()
			self.newsvf+=map(float,vals)
		self.activecnt=0
		for i in range(len(self.grids)):
			self.grids[i].active=False
		for i in range(len(self.newsvf)):
			if self.newsvf[i]!=0 and self.svfs[i]==0:
				self.grids[i].active=True
				self.activecnt+=1
		previous=-1
		while self.activecnt>0 and self.activecnt!=previous:
			previous=self.activecnt
			for i in range(len(newzones)):
				newzones[i]=self.Expand(newzones[i])
		return newzones

	def Compute(self,zone,thres):
		self.activecnt=0
		for i in range(len(self.grids)):
			self.grids[i].active=False
		if thres<1:
			if len(zone)<4 or self.IsAspectRatioInRange(zone):
				return [zone]
			else:
				for i in zone:
					self.grids[i].active=True
					self.activecnt+=1
				left=right=top=bottom=zone[0]
				for cell in zone:
					if cell/self.n < left/self.n: left = cell
					if cell/self.n > right/self.n: right = cell
					if cell%self.n < top%self.n: top = cell
					if cell%self.n > bottom%self.n: bottom = cell
				x=right/self.n-left/self.n
				y=bottom%self.n-top%self.n
				print x,y
				result=set()
				if x>self.side or y/float(x)<=self.ratio:
					result.add(left)
					result.add(right)
				if y>self.side or x/float(y)<=self.ratio:
					result.add(top)
					result.add(bottom)
				result=map(lambda x:[x],list(result))
				for r in result:
					self.grids[r[0]].active=False
				self.activecnt-=len(result)
				previous=-1
				while self.activecnt>0 or self.activecnt!=previous:
					previous=self.activecnt
					for i in range(len(result)):
						result[i]=self.Expand(result[i])
					if self.activecnt==previous and self.activecnt!=0:
						for i in range(len(self.grids)):
							if self.grids[i].active:
								result.append([i])
								self.grids[i].active=False
								self.activecnt-=1
								break
				newresult=[]
				for r in result:
					newresult+=self.Compute(r,0)
				return newresult
		for i in zone:
			boundary=False
			for p in range(-thres,thres+1):
				for q in range(-thres,thres+1):
					if i+p*self.n+q not in zone:
						boundary=True
						break
			if boundary:
				self.grids[i].val=0
				self.grids[i].active=True
				self.activecnt+=1
				continue
			self.grids[i].val=1
		zones=[]
		for i in zone:
			if self.grids[i].val==1:
				first=True
				firstzone=None
				j=0
				while j<len(zones):
					for grid in zones[j]:
						if self.IsAdjacent(grid,i):
							if first:
								zones[j].append(i)
								firstzone=zones[j]
								first=False
								break
							else:
								firstzone+=zones[j]
								del zones[j]
								break
					j+=1
				if first:
					zones.append([i])
		previous=-1
		while self.activecnt>0 or self.activecnt!=previous:
			previous=self.activecnt
			for i in range(len(zones)):
				zones[i]=self.Expand(zones[i])
			if self.activecnt==previous and self.activecnt!=0:
				for i in range(len(self.grids)):
					if self.grids[i].active:
						zones.append([i])
						self.grids[i].active=False
						self.activecnt-=1
						break
		result=[]
		for z in zones:
			if len(z)<4 or (self.IsAspectRatioInRange(z) and self.ConvexHull(z).GetArea()/(len(z)*100)<1.5):
				result.append(z)
			else:
				# print len(z), thres, len(result)
				rs=self.Compute(z,thres-1)
				# print len(z), thres, len(rs)
				result += rs
				# print len(z), thres, len(result)
		return result

	def ToOBJ(self,zones,height=0, name="zones.obj"):
		f = open(name, 'w')
		i=j=0
		for zone in zones:
			f.write("o {0}H{1}\n".format(i,height))
			for cell in zone:
				for pts in self.grids[cell].shape.points:
					f.write("v {0} {1} {2}\n".format(pts.x, pts.y, height))
				f.write("f {0}// {1}// {2}// {3}//\n".format(j*4+1, j*4+2,j*4+3,j*4+4))
				j+=1
			i=i+1
		f.close()

	def SaveInfo(self,num,**dict):
		"""self.SaveInfo(2,zonelists=[[[1,2,3],[2,3,4],[3,4,5]],[[1,3,5],[2,4,6]]],heights=[0,900])"""
		f=open("property.csv",'w')

		for i in range(len(dict["zonelists"][0])):
			f.write("Z{0}H{1},{2},{3}\n".format(i,0,len(dict["zonelists"][0][i])*100,len(dict["zonelists"][0][i])*100*dict["heights"][0]))
		for i in range(len(dict["zonelists"][1])):
			f.write("Z{0}H{1},{2},{3}\n".format(i,dict["heights"][0],len(dict["zonelists"][1][i])*100,len(dict["zonelists"][1][i])*100*dict["heights"][1]))
		f.close()
		f=open("zone_input.csv",'w')
		f.write("0,G,")
		for i in range(len(dict["zonelists"][0])):
			f.write("Z{0}H{1},".format(i,0))
		for i in range(len(dict["zonelists"][0])):
			f.write("Z{0}H{1},".format(i,dict["heights"][0]))
		f.write("B\n")
		f.write("0\t0,0\t0,")
		for zone in dict["zonelists"][0]:
			f.write("0\t{0},".format(self.CountNeighbour(zone,lambda x: (x%self.n<0 or x%self.n>=self.n or x/self.n<0 or x/self.n>=self.n))*10*dict["heights"][0]))
		for zone in dict["zonelists"][1]:
			f.write("{0}\t{1},".format(len(zone)*100,self.CountNeighbour(zone,lambda x: (x%self.n<0 or x%self.n>=self.n or x/self.n<0 or x/self.n>=self.n))*10*dict["heights"][1]))
		f.write("0\t0\n")
		f.write("0\t0,0\t0,")
		for zone in dict["zonelists"][0]:
			f.write("{0}\t0,".format(len(zone)*100))
		for zone in dict["zonelists"][1]:
			f.write("0\t0,")
		f.write("0\t0\n")
		for i1 in range(len(dict["zonelists"][0])):
			f.write("0\t0,0\t0,")
			for i2 in range(len(dict["zonelists"][0])):
				if i1==i2:
					f.write("0\t0,")
				else:
					f.write("0\t{0},".format(self.CountNeighbour(dict["zonelists"][0][i2],lambda x: (x in dict["zonelists"][0][i1]))*10*dict["heights"][0]))
			for i2 in range(len(dict["zonelists"][1])):
				if i1==i2:
					f.write("{0}\t0,".format(len(dict["zonelists"][0][i1])*100))
				else:
					f.write("0\t0,")
			f.write("0\t{0}\n".format(self.CountNeighbour(dict["zonelists"][0][i1],lambda x: self.svfs[x]==0)))
		for i1 in range(len(dict["zonelists"][1])):
			f.write("0\t0,0\t0,")
			for i2 in range(len(dict["zonelists"][0])):
				f.write("0\t0,")
			for i2 in range(len(dict["zonelists"][1])):
				if i1==i2:
					f.write("0\t0,")
				else:
					f.write("0\t{0},".format(self.CountNeighbour(dict["zonelists"][1][i2],lambda x: (x in dict["zonelists"][1][i1]))*10*dict["heights"][1]))
			f.write("{0}\t{1}\n".format((len(dict["zonelists"][1][i1])-len(dict["zonelists"][0][i1]))*100,self.CountNeighbour(dict["zonelists"][1][i1],lambda x: self.newsvf[x]==0)))
		for i in range(3+2*len(dict["zonelists"][0])):
			f.write("0\t0,")
		f.write("0\t0\n")
		f.close()

	def CountNeighbour(self,zone,func):
		"""count the number of neighbouring cells that satisfy the criteria described by func"""
		num=0
		for cell in zone:
			#right
			if (cell+1)%self.n > cell and func(cell+1):
				num+=1
			#left
			if (cell-1)%self.n < cell and func(cell-1):
				num+=1
			#top
			if (cell+self.n) < self.n * self.n and func(cell+self.n):
				num+=1
			#bottom
			if (cell-self.n) >= 0 and func(cell-self.n):
				num+=1
		return num


	def Draw(self, zones,name="zones.svg"):
		"""draw the each zone in zones with a random color and save the image as a svg file with the given name"""
		builder=TPPL.SVGBuilder()
		for zone in zones:
			r = random.randint(0xFF000000, 0xFFFFFFFF)
			grids=[]
			for grid in zone:
				grids.append(self.grids[grid].shape)
			builder.SetPolygons(grids,r,r)
		builder.SaveToFile(name)

	def IsAdjacent(self,i,j):
		"""Return True if j is within the neighbouring eight cells of i"""
		xi=i/self.n
		yi=i%self.n
		xj=j/self.n
		yj=j%self.n
		if (yi==yj+1 or yi==yj-1) and xj-1<=xi<=xj+1:
			return True
		if yi==yj and (xj==xi-1 or xj==xi+1):
			return True 
		return False

	def Expand(self,zone):
		"""Expand a zone into neighbouring active cells"""
		newzone=copy.deepcopy(zone)
		for cell in zone:
			i=cell/self.n
			j=cell%self.n
			for p in range(-1,2):
				for q in range(-1,2):
					if 0<=i+p<self.n and 0<=j+q<self.n:
						index=(i+p)*self.n+(j+q)
						if index not in newzone and self.grids[index].active:
							newzone.append(index)
							self.grids[index].active=False
							self.activecnt=self.activecnt-1
		return newzone

	def IsAspectRatioInRange(self,zone):
		"""True if the max vertical and horizontal difference is smaller than self.side and the ratio of max vertical and horizontal difference is within self.ratio"""
		left=right=zone[0]/self.n
		top=bottom=zone[0]%self.n
		for cell in zone:
			if cell/self.n < left: left = cell/self.n
			if cell/self.n > right: right = cell/self.n
			if cell%self.n < top: top = cell%self.n
			if cell%self.n > bottom: bottom = cell%self.n
		x=right-left
		y=bottom-top
		if x>self.side or y>self.side:
			return False
		if x<y:
			return x/float(y)>self.ratio
		else:
			return y/float(x)>self.ratio

	def ConvexHull(self,zone):
		"""return the convex hull of the given zone"""
		p = set()
		for cell in zone:
			for point in self.grids[cell].shape.points:
				p.add(point)
		p = list(p)
		if len(p) == 1 or len(p) == 2:
			poly=TPPL.Poly()
			for pts in p:
				poly.Append(pts)
			return poly
		def _orientation(p, q, r):
			'''Return positive if p-q-r are clockwise, neg if ccw, zero if
			collinear.'''
			return (q.y - p.y)*(r.x - p.x) - (q.x - p.x)*(r.y - p.y)
		# # scan to find upper and lower convex hulls of a set of 2d points.
		U = []
		L = []
		p.sort(key=lambda x: [x.x,x.y])
		for p_i in p:
			while len(U) > 1 and _orientation(U[-2], U[-1], p_i) <= 0:
				U.pop()
			while len(L) > 1 and _orientation(L[-2], L[-1], p_i) >= 0:
				L.pop()
			U.append(p_i)
			L.append(p_i)
		U.reverse()
		convexHull = L + U[1:-1]
		poly=TPPL.Poly()
		for pts in convexHull:
			poly.Append(pts)
		return poly
