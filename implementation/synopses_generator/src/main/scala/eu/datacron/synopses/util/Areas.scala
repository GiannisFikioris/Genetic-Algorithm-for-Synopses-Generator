/******************************************************************************
   * Project: datAcron
   * File: eu.datacron.synopses.util/Areas.scala
   * Description: Holds information for each ship id.
   * Developer: Kostas Patroumpas (UPRC)
   * Date: 3/9/2019
   * Revised: 3/9/2019
   ************************************************************************/

   package eu.datacron.synopses

   import scala.io.Source
   import eu.datacron.synopses.maritime.critical_point

   import org.locationtech.jts.io.WKTReader
   import org.locationtech.jts.geom.Polygon
   import org.locationtech.jts.geom.Geometry
   import org.locationtech.jts.geom.Coordinate
   import org.locationtech.jts.geom.GeometryFactory
  
   case class Areas(
      var Polys: Array[(Geometry,String)],        // List with Polygons and type of poly
      var MinX: Double,                           // Minimum X value
      var MaxX: Double,                           // Maximum X value
      var MinY: Double,                           // Minimum Y value
      var MaxY : Double,                          // Maximum Y value
      var Num : Int,                              // Size if spatial index grid
      var Index : Array[Array[Array[Int]]]        // Spatial Index
      )                      
  {
  
  
   //Constructor
   def this() {
      this(Array[(Geometry,String)](),0,0,0,0,0,Array[Array[Array[Int]]]())        //DEFAULT values
   }
  
  
   //Print out current properties
   override def toString: String = {
      val sb: StringBuilder = new StringBuilder
      sb.append(Polys.mkString(", ")).append(" | ")
      sb.append(MinX.toString).append(" | ")
      sb.append(MaxX.toString).append(" | ")
      sb.append(MinY.toString).append(" | ")
      sb.append(MaxY.toString).append(" | ")
      sb.append(Num.toString)
      sb.toString()
   }

   def getAreaType(x: Double, y: Double): String = {

      // If Num not positive, there are no areas
      if(Num <= 0)
         return null
      
      // X is outside of range, return not in any area
      if(x < MinX || x > MaxX)
         return null
   
      // Y is outside of range, return not in any area
      if(y < MinY || y > MaxY)
         return null

      // Calculate index for grid
      val i: Int = math.floor(Num * (x - MinX)/(MaxX - MinX)).toInt;
      val j: Int = math.floor(Num * (y - MinY)/(MaxY - MinY)).toInt;
      
      // Create point Geometry
      val p: Geometry = new GeometryFactory().createPoint(new Coordinate(x,y))

      // For each poly in the selected box
      for(k <- Index(i)(j)){
         // Check if point is in the polygon
         if(Polys(k)._1.contains(p))
            // If so return the poly type
            return Polys(k)._2
      }

      // Else return that point is not in any area
      return null
   }
   

   def initIndex(Polys: Array[(Geometry,String)], N: Int): Areas = {

      // Calculate minimum X value
      MinX = Polys.map(_._1.getCoordinates()
                        .map(_.getX())
                        .min)
                  .min

      // Calculate maximum X value
      MaxX = Polys.map(_._1.getCoordinates()
                        .map(_.getX())
                        .max)
                  .max

      // Calculate minimum Y value
      MinY = Polys.map(_._1.getCoordinates()
                        .map(_.getY())
                        .min)
                  .min

      // Calculate maximum Y value
      MaxY = Polys.map(_._1.getCoordinates()
                        .map(_.getY())
                        .max)
                  .max

      // Create grid
      Num = N
      Index = Array.ofDim[Array[Int]](Num, Num)

      // Find the width and length of each rectange in the grid
      val xStep = (MaxX-MinX)/Num
      val yStep = (MaxY-MinY)/Num

      val geomFact = new GeometryFactory() 

      // For each rect in the grid
      for (i <- 0 until N; j<- 0 until N){

         // Calculate one point of the grid as (x, y)
         // the other point is simply (x+xStep, y+yStep)
         val x = MinX + i*xStep
         val y = MinY + i*yStep

         // Create the 4 points of current rectangle
         val shell = Array(
            new Coordinate(x        , y),
            new Coordinate(x + xStep, y),
            new Coordinate(x + xStep, y + yStep),
            new Coordinate(x        , y + yStep),
            new Coordinate(x        , y)
         )

         // Create the rectange as a JTS geometry
         val g: Geometry = geomFact.createPolygon(shell)
         
         // Initialize the current rectangle's list that holds the indexes of the polygons
         // that intersect with the rectangle
         Index(i)(j) = Array[Int]()

         // For each poly check for intersection with the rectangle and save the right indexes
         for(k <- 0 until Polys.length){
            if(Polys(k)._1.intersects(g))
               Index(i)(j) :+= k
         }
         
      }

      Areas(Polys,MinX,MaxX,MinY,MaxY,Num,Index) // Initialize instance 
   }
  
  
    // Read a configuration from settings stored in a properties file
   def fromFile(propertiesFile: String, N : Int): Areas = {

      // Non positive N means that no areas will be used
      if(N<=0)
         return new Areas()

      // Initialize Reader
      val wktReader = new WKTReader();
      
      // Read polys from the file
      Polys = Source.fromFile(propertiesFile)
                    .getLines()
                    .filter(!_.isEmpty())
                    .toArray
                    .map({ x => (wktReader.read(x.split(";")(0)), // Create a tuple where the first element is the poly,
                                 x.split(";")(1).trim)                 // and the second element is the type of poly
                        })

      if(Polys.size == 0)
         return new Areas()

      initIndex(Polys, N) // Create Index and return new Areas
   }
  
  }
  