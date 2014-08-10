import copy
import math
import TPPL
import random

#not included: exception handling, especially when input is out of bound or of different type than expected

class GridCell:
	def __init__(self,shape=None,normal=(0,0,1),val=None,active=False):
		self.shape=shape
		self.val=val
		self.normal=normal
		self.active=active

class SVFGrid:
	def __init__(self,thres,side,ratio,numlayer,heights):
		self.grids=[]
		self.activecnt=0
		self.svfs=[]
		self.ratio=ratio
		self.svfs=[map(float,line.strip().split()) for line in open("./svf_0.txt","r")]
		self.n=len(self.svfs)
		self.svfs=[item for sublist in self.svfs for item in sublist] #flatten the list of lists
		#read in the x, y coordinate of the points and normals
		vals = [map(float,line.strip().split()) for line in open('./0.pts')]
		self.interval=math.fabs(vals[0][1]-vals[1][1])
		self.side=side*self.n
		zone=[]
		for i in range(len(self.svfs)):
			self.grids.append(GridCell(TPPL.Poly().Square(TPPL.Point(vals[i][0]-self.interval/2.0,vals[i][1]-self.interval/2.0),self.interval),(vals[i][3],vals[i][4],vals[i][5])))
			if self.svfs[i]>0:
				zone.append(i)
		zones=self.Compute(zone,thres)
		self.Draw(zones)
		zonelists=[]
		zonelists.append(zones)
		for i in range(1,numlayer):
			self.svfs=[map(float,line.strip().split()) for line in open("./svf_{0}.txt".format(i),"r")]
			self.svfs=[item for sublist in self.svfs for item in sublist] #flatten the list of lists
			zones=copy.deepcopy(zonelists[i-1])
			z=[]
			for j in range(len(self.svfs)):
				if self.svfs[j]==0:
					for zone in zones:
						if j in zone:
							zone.remove(j)
				elif not any(j in l for l in zonelists[i-1]):
					z.append(j)
					self.grids[j].val=-1
			zones+=self.Compute(z,thres)
			zonelists.append(zones)
		for i in range(numlayer):
			self.Draw(zonelists[i],"layer_{0}.svg".format(i))
			self.ToOBJ(zonelists[i],heights[i],"layer_{0}.obj".format(i),heights[i])
		# self.SaveInfo(numlayer,zonelists,heights)
		# print self.vals
		# Draw(self.grids,"grid.svg")

	def Compute(self,zone,thres):
		self.activecnt=0
		for grid in self.grids:
			grid.active=False
		if thres<1:
			if self.IsAspectRatioInRange(zone):
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
				print x, y
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
			if self.IsAspectRatioInRange(z) and self.ConvexHull(z).GetArea()/(len(z)*100)<1.5:
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

	def SaveInfo(self,num,zonelists,heights):
		"""self.SaveInfo(2,zonelists=[[[1,2,3],[2,3,4],[3,4,5]],[[1,3,5],[2,4,6]]],heights=[0,900])"""
		f=open("property.csv",'w')

		for i in range(len(zonelists[0])):
			f.write("Z{0}H{1},{2},{3}\n".format(i,0,len(zonelists[0][i])*100,len(zonelists[0][i])*100*heights[0]))
		for i in range(len(zonelists[1])):
			f.write("Z{0}H{1},{2},{3}\n".format(i,heights[0],len(zonelists[1][i])*100,len(zonelists[1][i])*100*heights[1]))
		f.close()
		f=open("zone_input.csv",'w')
		f.write("0,G,")
		for i in range(len(zonelists[0])):
			f.write("Z{0}H{1},".format(i,0))
		for i in range(len(zonelists[0])):
			f.write("Z{0}H{1},".format(i,heights[0]))
		f.write("B\n")
		f.write("0\t0,0\t0,")
		for zone in zonelists[0]:
			f.write("0\t{0},".format(self.CountNeighbour(zone,lambda x: (x%self.n<0 or x%self.n>=self.n or x/self.n<0 or x/self.n>=self.n))*10*heights[0]))
		for zone in zonelists[1]:
			f.write("{0}\t{1},".format(len(zone)*100,self.CountNeighbour(zone,lambda x: (x%self.n<0 or x%self.n>=self.n or x/self.n<0 or x/self.n>=self.n))*10*heights[1]))
		f.write("0\t0\n")
		f.write("0\t0,0\t0,")
		for zone in zonelists[0]:
			f.write("{0}\t0,".format(len(zone)*100))
		for zone in zonelists[1]:
			f.write("0\t0,")
		f.write("0\t0\n")
		for i1 in range(len(zonelists[0])):
			f.write("0\t0,0\t0,")
			for i2 in range(len(zonelists[0])):
				if i1==i2:
					f.write("0\t0,")
				else:
					f.write("0\t{0},".format(self.CountNeighbour(zonelists[0][i2],lambda x: (x in zonelists[0][i1]))*10*heights[0]))
			for i2 in range(len(zonelists[1])):
				if i1==i2:
					f.write("{0}\t0,".format(len(zonelists[0][i1])*100))
				else:
					f.write("0\t0,")
			f.write("0\t{0}\n".format(self.CountNeighbour(zonelists[0][i1],lambda x: self.svfs[x]==0)))
		for i1 in range(len(zonelists[1])):
			f.write("0\t0,0\t0,")
			for i2 in range(len(zonelists[0])):
				f.write("0\t0,")
			for i2 in range(len(zonelists[1])):
				if i1==i2:
					f.write("0\t0,")
				else:
					f.write("0\t{0},".format(self.CountNeighbour(zonelists[1][i2],lambda x: (x in zonelists[1][i1]))*10*heights[1]))
			f.write("{0}\t{1}\n".format((len(zonelists[1][i1])-len(zonelists[0][i1]))*100,self.CountNeighbour(zonelists[1][i1],lambda x: self.svfs[x]==0)))
			# f.write("{0}\t{1}\n".format((len(zonelists[1][i1])-len(zonelists[0][i1]))*100,self.CountNeighbour(zonelists[1][i1],lambda x: self.newsvf[x]==0)))
		for i in range(3+2*len(zonelists[0])):
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
		x=right-left+1
		y=bottom-top+1
		if x<4 or y<4:
			return True
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
