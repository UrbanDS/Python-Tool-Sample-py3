"""
the canvas to draw the shapefile and interaction with mouse clicks
"""
from tkinter import Toplevel, Canvas
from shp_reader import SHP_TYPE_POINT,SHP_TYPE_LINE,SHP_TYPE_POLYGON,Polygon

# display parameters
canvasWidth, canvasHeight,margin_x, margin_y  = 800, 600, 100, 100
    
class MainCanvas(object):
    """
    The shapefile displaying device based on TKinter Canvas

    Attributes
    ----------

    shapes           : array
                      The spatial units
    bbox             : array
                      The bounding box: minX, minY, maxX, maxY
    shp_type         : integer
                      The shape types: SHP_TYPE_POINT,SHP_TYPE_LINE,SHP_TYPE_POLYGON
    root             : Tk
                      The Tk Object
    attributeName    : string
                      The attribute name
    datalist         : array
                      The attribute data
                      
    """
    def __init__(self,shapes,bbox,shp_type,root,attributeName,datalist):
        self.shapes = shapes
        self.bbox = bbox
        self.shp_type = shp_type
        self.root = root
        self.attributeName = attributeName
        self.datalist = datalist

        self.__createCanvas()
         
    def __createCanvas(self):
        """
        Create the canvas and draw all the spatial objects
        """ 
        self.canvasRoot = Toplevel()
        self.canvasRoot.title(self.attributeName)
        self.canvasRoot.lower(belowThis = self.root)
        self.mainCanvas = Canvas(self.canvasRoot, bg = 'white', width = canvasWidth+margin_x, height = canvasHeight+margin_y, scrollregion=('-50c','-50c',"50c","50c") )
        self.__drawShape()
        self.mainCanvas.pack()
        
    def __drawShape(self):
        """
        Draw all the spatial objects on the canvas
        """
        minX, minY, maxX, maxY = self.bbox[0],self.bbox[1],self.bbox[2],self.bbox[3]
        # calculate ratios of visualization
        ratiox = canvasWidth/(maxX-minX)
        ratioy = canvasHeight/(maxY-minY)
        # take the smaller ratio of window size to geographic distance
        ratio = ratiox
        if ratio>ratioy:
            ratio = ratioy
            
        if self.shp_type == SHP_TYPE_POINT:
            self.__drawPoints(minX, minY, maxX, maxY, ratio)
        elif self.shp_type == SHP_TYPE_LINE:
            self.__drawPolylines(minX, minY, maxX, maxY, ratio)
        elif self.shp_type == SHP_TYPE_POLYGON:
            self.__drawPolygons(minX, minY, maxX, maxY, ratio)
      
    def __drawPoints(self,minX, minY, maxX, maxY,ratio):
        """
        Draw points on the canvas
        """  
        tag_count = 0
        # loop through each point
        for point in self.shapes:
            #define an empty xylist for holding converted coordinates
            x = int((point.x-minX)*ratio)+margin_x/2
            y = int((maxY-point.y)*ratio)+margin_y/2
            _point = self.mainCanvas.create_oval(x-2, y-2, x+2, y+2, outline=point.color, 
                               fill=point.color, width=2, tags = self.datalist[tag_count])
            self.mainCanvas.tag_bind( _point, '<ButtonPress-1>', self.__showAttriInfo)  
            tag_count += 1
        
    def __drawPolylines(self,minX, minY, maxX, maxY,ratio):
        """
        Draw polylines on the canvas
        """     
        tag_count = 0
        # loop through each polyline
        for polyline in self.shapes:
            #define an empty xylist for holding converted coordinates
            xylist = []
            # loops through each point and calculate the window coordinates, put in xylist
            for j in range(len(polyline.x)):
                pointx = int((polyline.x[j]-minX)*ratio)+margin_x/2
                pointy = int((maxY-polyline.y[j])*ratio)+margin_y/2
                xylist.append(pointx)
                xylist.append(pointy)
            # loop through each part of the polyline
            for k in range(polyline.partsNum):
                #get the end sequence number of points in the part
                if (k==polyline.partsNum-1):
                    endPointIndex = len(polyline.x)
                else:
                    endPointIndex = polyline.partsIndex[k+1]
                # define a temporary list for holding the part coordinates
                tempXYlist = []
                #take out points' coordinates for the part and add to the temporary list
                for m in range(polyline.partsIndex[k], endPointIndex):
                    tempXYlist.append(xylist[m*2])
                    tempXYlist.append(xylist[m*2+1])
                # create the line
                _line = self.mainCanvas.create_line(tempXYlist,fill=polyline.color, tags = self.datalist[tag_count])
                self.mainCanvas.tag_bind( _line, '<ButtonPress-1>', self.__showAttriInfo)            
            tag_count += 1
  
    def __drawPolygons(self,minX, minY, maxX, maxY,ratio):
        """
        Draw polygons on the canvas
        """      
        tag_count = 0
        for polygon in self.shapes:
            #define an empty xylist for holding converted coordinates
            xylist = []
            # loops through each point and calculate the window coordinates, put in xylist
            for point in polygon.points:
                pointx = int((point.x -minX)*ratio) + +margin_x/2
                pointy = int((maxY- point.y)*ratio) + +margin_y/2
                xylist.append(pointx)
                xylist.append(pointy)
            """
            polyline.partsIndex is a tuple data type holding the starting points for each
            part. For example, if the polyline.partsIndex of a polyline equals to (0, 4, 9),
            and the total points, which is calcuate by len(polyline.points) equals to 13.
            This means that the polyline has three parts, and the each part would have the points
            as follows.
            
            part 1: p0,p1,p2,p3
            part 2: p4,p5,p6,p7,p8
            part 3: p9,p10,p11,p12
            
            The xylist would be:
            xylist = [x0, y0, x1, y1, x2, y2, x3, y3, x4, y4....x12, y12]
            where 
            xylist[0] = x0
            xylist[1] = y0
            xylist[2] = x1
            xylist[3] = y1
            .....
            
            To draw the first part of polyline, we want to get tempXYlist as
        
            tempXYlist = [x0, y0, x1, y1, x2, y2, x3, y3]
            
            At this time, m is in range(0,4)
            
            xylist[m*2] would be is x0(when m=0), x1(when m=1), x2(when m=2), x3(when m=3)
        
            xylist[m*2+1] would be is y0(when m=0), y1(when m=1), y2(when m=2), y3(when m=3)
            """
            for k in range(polygon.partsNum):
                #get the end sequence number of points in the part
                if (k==polygon.partsNum-1):
                    endPointIndex = len(polygon.points)
                else:
                    endPointIndex = polygon.partsIndex[k+1]
         
                #Define a temporary list for holding the part coordinates
                tempXYlist = []
                #take out points' coordinates for the part and add to the temporary list
                for m in range(polygon.partsIndex[k], endPointIndex):            
                    tempXYlist.append(xylist[m*2])
                    tempXYlist.append(xylist[m*2+1])
                startIndex = polygon.partsIndex[k] #start index for our positive polygon. 
                tempPoints = polygon.points[startIndex: endPointIndex]#we get our temppoints to help use create our polygon using positive data
                newPolygon = Polygon(tempPoints) #here we create our polygons using positve data
                area = newPolygon.getArea() # Calculate the area
                if area > 0:
                    _polygon = self.mainCanvas.create_polygon(tempXYlist,fill=polygon.color,outline="black",tags = self.datalist[tag_count])#creating our polygon outline
                else:
                    # If it is a hole, fill with the same color as the canvas background color 
                    _polygon = self.mainCanvas.create_polygon(tempXYlist,fill="white",outline="black", tags = self.datalist[tag_count])
                self.mainCanvas.tag_bind( _polygon, '<ButtonPress-1>', self.__showAttriInfo)            
            tag_count += 1
                
    def __showAttriInfo(self,event):
        """
        Show attribute information of clicked unit
        """        
        widget_id=event.widget.find_closest(event.x, event.y) 
        print("click!!!!", widget_id)
        print(self.attributeName.decode()+" is: "+self.mainCanvas.gettags(widget_id)[0])