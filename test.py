import polypartition
import math
#import PIL.ImageDraw as ImageDraw,PIL.Image as Image, PIL.ImageShow as ImageShow
#from numpy import random

scale = 1


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
    
    def AddPolygon(self, poly, brushColor, penColor):
        if poly is None or len(poly) == 0: return
        pi = self.StyleInfoPlus()
        pi.penWidth = self.GlobalStyle.penWidth
        pi.showCoords = self.GlobalStyle.showCoords
        pi.brushClr = brushColor
        pi.penClr = penColor        
        pi.polygons.append(poly)
        self.PolyInfoList.append(pi)
    
    def AddPolygons(self, polys, brushColor, penColor):
        if polys is None or len(polys) == 0: return
        pi = self.StyleInfoPlus()
        pi.penWidth = self.GlobalStyle.penWidth
        pi.showCoords = self.GlobalStyle.showCoords
        pi.brushClr = brushColor
        pi.penClr = penColor        
        pi.polygons = polys
        self.PolyInfoList.append(pi)
    
    def SaveToFile(self, filename, invScale = 1.0, margin = 10):
        if len(self.PolyInfoList) == 0: return False
        if invScale == 0: invScale = 1.0
        if margin < 0: margin = 0
        pi = self.PolyInfoList[0]
        # get bounding rect ...
        left = right = pi.polygons[0].GetPoint(0).getX()
        top = bottom = pi.polygons[0].GetPoint(0).getY()
        for pi in self.PolyInfoList:
            for p in pi.polygons:
                for i in range(0,p.GetNumPoints()):
                    if p.GetPoint(i).getX() < left: left = p.GetPoint(i).getX()
                    if p.GetPoint(i).getX() > right: right = p.GetPoint(i).getX()
                    if p.GetPoint(i).getY() < top: top = p.GetPoint(i).getY()
                    if p.GetPoint(i).getY() > bottom: bottom = p.GetPoint(i).getY()
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
                cnt = p.GetNumPoints()
                if cnt < 3: continue
                f.write(" M {0:.2f} {1:.2f}".format(p.GetPoint(0).getX() * invScale + offsetX, p.GetPoint(0).getY() * invScale + offsetY))
                for i in range(1,cnt):
                    f.write(" L {0:.2f} {1:.2f}".format(p.GetPoint(i).getX() * invScale + offsetX, p.GetPoint(i).getY() * invScale + offsetY))
                f.write(" z")
            fillRule = "evenodd"
            f.write(self.PathFooter.format(self.HtmlColor(pi.brushClr), 
                self.AlphaClr(pi.brushClr), fillRule, 
                self.HtmlColor(pi.penClr), self.AlphaClr(pi.penClr),  pi.penWidth))
    
        f.write("</svg>\n")
        f.close()
        return True
##
##def DrawPolyList(polys):
##	xmin = 0
##	ymin = 0
##	xmax = 0
##	ymax = 0
##	for poly in polys:
##		for i in range(0,poly.GetNumPoints()):
##			if (poly.GetPoint(i).getX()>xmax):
##				xmax=poly.GetPoint(i).getX()
##			if (poly.GetPoint(i).getX()<xmin):
##				xmin=poly.GetPoint(i).getX()
##			if (poly.GetPoint(i).getY()>ymax):
##				ymax=poly.GetPoint(i).getY()
##			if (poly.GetPoint(i).getY()<ymin):
##				ymin=poly.GetPoint(i).getY()
##	xmin=scale*xmin-10
##	ymin=scale*ymin-10
##	xmax=scale*xmax+10
##	ymax=scale*ymax+10
##	im=Image.new("RGB",(int(xmax-xmin),int(ymax-ymin)))
##	draw = ImageDraw.Draw(im)
##	for poly in polys:
##		l=list()
##		for i in range(0,poly.GetNumPoints()):
##			l.append((poly.GetPoint(i).getX()*scale-xmin,poly.GetPoint(i).getY()*scale-ymin));
##		draw.polygon(tuple(l),fill=(random.random_integers(0,255),random.random_integers(0,255),random.random_integers(0,255)))
##	im.show()

def ReadPoly(f):
	p=polypartition.TPPLPoly()
	n=int(f.readline())
	p.Init(n)
	hole=int(f.readline())>0
	p.SetHole(hole)
	for i in range(0,n):
		line=f.readline()
		vals=line.split()
		p.SetPoint(i,int(vals[0]),int(vals[1]))
	if((p.GetOrientation()==polypartition.TPPL_CCW) == hole):
		p.Invert()
	return p


def ReadPolyList(filename):
	f=open(filename,"r")
	l=polypartition.listpoly()
	for i in range(0,int(f.readline())):
		l.append(ReadPoly(f))
	return l

scaleExp = 2.2
scale = math.pow(10, scaleExp)
invScale = 1.0 / scale
l=ReadPolyList("test2.txt")
result=polypartition.listpoly()
result2=polypartition.listpoly()
pa=polypartition.TPPLPartition()
pa.ConvexPartition_HM(l,result)
pa.Triangulate_EC(l,result2)
print result[0].GetPoints()
# DrawPolyList(l)
svgBuilder = SVGBuilder()
svgBuilder.GlobalStyle.penWidth = 0.6
svgBuilder.AddPolygons(l, 0x60138013, 0xFF003300)
svgBuilder.SaveToFile('./original.svg', invScale, 100)
svgBuilder = SVGBuilder()
svgBuilder.GlobalStyle.penWidth = 0.6
svgBuilder.AddPolygons(result, 0x60138013, 0xFF003300)
svgBuilder.SaveToFile('./partition.svg', invScale, 100)
svgBuilder = SVGBuilder()
svgBuilder.GlobalStyle.penWidth = 0.6
svgBuilder.AddPolygons(result2, 0x60138013, 0xFF003300)
svgBuilder.SaveToFile('./triangulation.svg', invScale, 100)

f = open("zones.obj", 'w')
i=0
for res in result:
    f.write("o {0}\n".format(i))
    for j in range(0,res.GetNumPoints()):
        f.write("v {0} {1} 0\n".format(res.GetPoint(j).getX(), res.GetPoint(j).getY() ))
    for j in range(0,res.GetNumPoints()):
        f.write("v {0} {1} 100000\n".format(res.GetPoint(j).getX(), res.GetPoint(j).getY() ))
    f.write("f")
    for j in range(0,res.GetNumPoints()):
        f.write(" {0}//".format(i+j+1))
    f.write("\n")
    # f.write("f {0}// {1}// {2}//\n".format(i+res.GetNumPoints()-2, i+res.GetNumPoints()-1,i+1))
    # f.write("f {0}// {1}// {2}//\n".format(i+res.GetNumPoints()-1, i+1, i+2))
    i=i+res.GetNumPoints()
    f.write("f")
    for j in range(0,res.GetNumPoints()):
        f.write(" {0}//".format(i+j+1))
    f.write("\n")
    for j in range(0,res.GetNumPoints()-1):
        f.write("f {0}// {1}// {2}// {3}//\n".format(i+j+1, i+j+2,i+j+2-res.GetNumPoints(), i+j+1-res.GetNumPoints()))
    # f.write("f {0}// {1}// {2}//\n".format(i+res.GetNumPoints()-2, i+res.GetNumPoints()-1,i+1))
    # f.write("f {0}// {1}// {2}//\n".format(i+res.GetNumPoints()-1, i+1, i+2))
    # for j in range(0,res.GetNumPoints()):
    #     f.write("f {0}// {1}// {2}//".format(i+j-, i+j+2,i+j+3))
    i=i+res.GetNumPoints()
f.close()
