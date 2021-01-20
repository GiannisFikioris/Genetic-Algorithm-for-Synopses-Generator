/******************************************************************************
  * Project: datAcron
  * File: eu.datacron.synopses.util/Parametrization.scala
  * Description: Holds parameters used in maintenance of trajectory synopses.
  * Developer: Kostas Patroumpas (UPRC)
  * Date: 20/12/2016
  * Revised: 3/6/2017
  ************************************************************************/

package eu.datacron.synopses

import java.util.Properties
import org.apache.flink.api.java.utils.ParameterTool
import eu.datacron.synopses.maritime.critical_point

/**
  * Configuration defines basic parameters for use during trajectory summarization, i.e., for detection and characterization of critical points along each trajectory.
  *
  * @param DISTANCE_THRESHOLD_V => 5.0F        //meters
  * @param ANGLE_THRESHOLD_V => 5.0F           //degrees
  * @param GAP_PERIOD_V => 600L                //seconds
  * @param HISTORY_PERIOD_V => 1000L           //seconds
  * @param BUFFER_SIZE_V => 5                  //number of most recent raw point locations to be used in velocity vector computations
  * @param ANGLE_NOISE_THRESHOLD_V => 120.0F   //turn more than this angle should be considered as noise
  * @param CLIMB_THRESHOLD_V => 5.0F           //feet per second
  * @param CLIMB_NOISE_THRESHOLD_V => 100.0F   //feet per second
  * @param SPEED_RATIO_V => 0.25F              //percentage: acceleration or deceleration by more than 25%
  * @param NO_SPEED_THRESHOLD_V => 1.0F        //knots (1 knot = 1.852 kmh)
  * @param LOW_SPEED_THRESHOLD_V => 1.0F       //knots (1 knot = 1.852 kmh)
  * @param MAX_SPEED_THRESHOLD_V => 30.0F      //knots (1 knot = 1.852 kmh)
  * @param MAX_RATE_OF_CHANGE_V => 100.0F      //knots per hour
  * @param MAX_RATE_OF_TURN_V => 3.0F          //degrees (azimuth) per second
  * @param MAX_ALTITUDE_STOP_V => 200.0F       //feet
  **/

case class Parametrization(
      var DISTANCE_THRESHOLD_V: Array[Double],           // meters
      var ANGLE_THRESHOLD_V: Array[Double],              // degrees
      var GAP_PERIOD_V: Array[Long],                     // seconds (UNIX epochs)
      var HISTORY_PERIOD_V: Array[Long],                 // seconds (UNIX epochs): period for which older positions will be held for velocity vector computations
      var BUFFER_SIZE_V: Array[Int],                     // number of most recent point locations to be used in velocity vector calculation
      var ANGLE_NOISE_THRESHOLD_V: Array[Double],        // degrees
      var CLIMB_THRESHOLD_V: Array[Double],              // feet per second
      var CLIMB_NOISE_THRESHOLD_V: Array[Double],        // feet per second
      var SPEED_RATIO_V: Array[Double],                  // percentage (%): acceleration or deceleration by more than SPEED_RATIO between two successive locations
      var NO_SPEED_THRESHOLD_V: Array[Double],           // threshold in knots (1 knot = 1.852 kmh)
      var LOW_SPEED_THRESHOLD_V: Array[Double],          // threshold in knots (1 knot = 1.852 kmh)
      var MAX_SPEED_THRESHOLD_V: Array[Double],          // threshold in knots (1 knot = 1.852 kmh)
      var MAX_RATE_OF_CHANGE_V: Array[Double],           // knots per hour
      var MAX_RATE_OF_TURN_V: Array[Double],             // degrees (azimuth) per second
      var MAX_ALTITUDE_STOP_V: Array[Double],            // feet
      var TYPE_V: Map[String, Int],                      // list of types of ship
      var AREAS_V: Areas)                                // object that holds the areas of interest
{


  //Constructor
  def this() {
    this(Array(5.0F), Array(5.0F), Array(600L), Array(1000L), Array(5), Array(120.0F), Array(5.0F), Array(200.0F), Array(0.25F), Array(1.0F), Array(1.0F), Array(30.0F), Array(100.0F), Array(3.0F), Array(200.0F), Map("def_" -> 0), new Areas())        //DEFAULT values
  }


  //Print out current properties
  override def toString: String = {
    val sb: StringBuilder = new StringBuilder
    sb.append(DISTANCE_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(ANGLE_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(GAP_PERIOD_V.mkString(", ")).append(" | ")
    sb.append(HISTORY_PERIOD_V.mkString(", ")).append(" | ")
    sb.append(BUFFER_SIZE_V.mkString(", ")).append(" | ")
    sb.append(ANGLE_NOISE_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(CLIMB_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(CLIMB_NOISE_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(SPEED_RATIO_V.mkString(", ")).append(" | ")
    sb.append(NO_SPEED_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(LOW_SPEED_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(MAX_SPEED_THRESHOLD_V.mkString(", ")).append(" | ")
    sb.append(MAX_RATE_OF_CHANGE_V.mkString(", ")).append(" | ")
    sb.append(MAX_RATE_OF_TURN_V.mkString(", ")).append(" | ")
    sb.append(MAX_ALTITUDE_STOP_V.mkString(", ")).append(" | ")
    sb.append(TYPE_V.toString).append(" | ")
    sb.append(AREAS_V.toString)
    sb.toString()
  }




   // Add a value in the arrays from a ParameterTool
   def addParamsFromParamTools(parameters: ParameterTool) {
      DISTANCE_THRESHOLD_V :+= parameters.get("val_DISTANCE_THRESHOLD").toDouble        //meters
      ANGLE_THRESHOLD_V :+= parameters.get("val_ANGLE_THRESHOLD").toDouble              //degrees
      GAP_PERIOD_V :+= parameters.get("val_GAP_PERIOD").toLong                            //seconds
      HISTORY_PERIOD_V :+= parameters.get("val_HISTORY_PERIOD").toLong                    //seconds
      BUFFER_SIZE_V :+= parameters.get("val_BUFFER_SIZE").toInt                            //number of most recent point locations to be used in velocity vector computations
      ANGLE_NOISE_THRESHOLD_V :+= parameters.get("val_ANGLE_NOISE_THRESHOLD").toDouble  //degrees
      CLIMB_THRESHOLD_V :+= parameters.get("val_CLIMB_THRESHOLD").toDouble              //feet per second
      CLIMB_NOISE_THRESHOLD_V :+= parameters.get("val_CLIMB_NOISE_THRESHOLD").toDouble  //feet per second
      SPEED_RATIO_V :+= parameters.get("val_SPEED_RATIO").toDouble                      //percentage
      NO_SPEED_THRESHOLD_V :+= parameters.get("val_NO_SPEED_THRESHOLD").toDouble        //knots
      LOW_SPEED_THRESHOLD_V :+= parameters.get("val_LOW_SPEED_THRESHOLD").toDouble      //knots
      MAX_SPEED_THRESHOLD_V :+= parameters.get("val_MAX_SPEED_THRESHOLD").toDouble      //knots
      MAX_RATE_OF_CHANGE_V :+= parameters.get("val_MAX_RATE_OF_CHANGE").toDouble        //knots per hour
      MAX_RATE_OF_TURN_V :+= parameters.get("val_MAX_RATE_OF_TURN").toDouble            //degrees (azimuth) per second
      MAX_ALTITUDE_STOP_V :+= parameters.get("val_MAX_ALTITUDE_STOP").toDouble          //feet
   }

   // Add a value in the arrays from a Properties
   def addParamsFromProperties(parameters: Properties) {
      DISTANCE_THRESHOLD_V :+= parameters.getProperty("val_DISTANCE_THRESHOLD").toDouble        //meters
      ANGLE_THRESHOLD_V :+= parameters.getProperty("val_ANGLE_THRESHOLD").toDouble              //degrees
      GAP_PERIOD_V :+= parameters.getProperty("val_GAP_PERIOD").toLong                          //seconds
      HISTORY_PERIOD_V :+= parameters.getProperty("val_HISTORY_PERIOD").toLong                  //seconds
      BUFFER_SIZE_V :+= parameters.getProperty("val_BUFFER_SIZE").toInt                         //number of most recent point locations to be used in velocity vector computations
      ANGLE_NOISE_THRESHOLD_V :+= parameters.getProperty("val_ANGLE_NOISE_THRESHOLD").toDouble  //degrees
      CLIMB_THRESHOLD_V :+= parameters.getProperty("val_CLIMB_THRESHOLD").toDouble              //feet per second
      CLIMB_NOISE_THRESHOLD_V :+= parameters.getProperty("val_CLIMB_NOISE_THRESHOLD").toDouble  //feet per second
      SPEED_RATIO_V :+= parameters.getProperty("val_SPEED_RATIO").toDouble                      //percentage
      NO_SPEED_THRESHOLD_V :+= parameters.getProperty("val_NO_SPEED_THRESHOLD").toDouble        //knots
      LOW_SPEED_THRESHOLD_V :+= parameters.getProperty("val_LOW_SPEED_THRESHOLD").toDouble      //knots
      MAX_SPEED_THRESHOLD_V :+= parameters.getProperty("val_MAX_SPEED_THRESHOLD").toDouble      //knots
      MAX_RATE_OF_CHANGE_V :+= parameters.getProperty("val_MAX_RATE_OF_CHANGE").toDouble        //knots per hour
      MAX_RATE_OF_TURN_V :+= parameters.getProperty("val_MAX_RATE_OF_TURN").toDouble            //degrees (azimuth) per second
      MAX_ALTITUDE_STOP_V :+= parameters.getProperty("val_MAX_ALTITUDE_STOP").toDouble          //feet
   }

   // Empty all the arrays
   def emptyArrays(){
      DISTANCE_THRESHOLD_V = Array[Double]()
      ANGLE_THRESHOLD_V = Array[Double]()
      GAP_PERIOD_V = Array[Long]()
      HISTORY_PERIOD_V = Array[Long]()
      BUFFER_SIZE_V = Array[Int]()
      ANGLE_NOISE_THRESHOLD_V = Array[Double]()
      CLIMB_THRESHOLD_V = Array[Double]()
      CLIMB_NOISE_THRESHOLD_V = Array[Double]()
      SPEED_RATIO_V = Array[Double]()
      NO_SPEED_THRESHOLD_V = Array[Double]()
      LOW_SPEED_THRESHOLD_V = Array[Double]()
      MAX_SPEED_THRESHOLD_V = Array[Double]()
      MAX_RATE_OF_CHANGE_V = Array[Double]()
      MAX_RATE_OF_TURN_V = Array[Double]()
      MAX_ALTITUDE_STOP_V = Array[Double]()
   }


  //Apply a configuration from settings stored in a properties file
   def fromFile(propertiesFile: String): Parametrization = {

      try {
         // Open properties file
         val parameters: ParameterTool = ParameterTool.fromPropertiesFile(propertiesFile)
         
         // Read the list of the ship types (comma separated)
         val types: String = parameters.get("val_SHIP_TYPES")

         emptyArrays() // Empty the arrays holding the default values 
         var i = 0

         if(types == null){
            // If types is null, then the old format is used and we read the params
            // from the current file (they are placed under the name "def_")
            TYPE_V = Map[String,Int]("def_" -> 0)
            addParamsFromParamTools(parameters)
         }
         else {
            // Else if the list of ship types is found, for each type there is a param
            // with the location of the file that holds the parameters for said type
            // eg if the type is "ship1" then there is a param with the name "file_ship1"
            // having the location of the new parameter file
            TYPE_V = Map[String,Int]("def_" -> 0)
            types.split(",").foreach{ e =>
               val name = e.trim // Trim starting and ending spaces
               TYPE_V += (name -> i) // Add name to dictionary
               // Open parameter file with the type parameters
               val params2 = ParameterTool.fromPropertiesFile(parameters.get("file_" + name))
               // Read Parameters from read parameter file
               addParamsFromParamTools(params2)
               i+=1
            }
         }

         // Initialize new Areas Instance
         AREAS_V = new Areas()
         
         // Find the location of the areas file
         val areas_file: String = parameters.get("file_AREAS")
         
         if(areas_file != null) {
            // If file is found then initialize areas from file
            AREAS_V = AREAS_V.fromFile(areas_file, 10)

            val area_types = parameters.get("val_AREA_TYPES")
            if(area_types == null)
               throw new RuntimeException("Invalid parametrization")

            area_types.split(",").foreach{ e =>
               val name = e.trim // Trim starting and ending spaces
               TYPE_V += (name -> i) // Add name to dictionary
               // Open parameter file with the type parameters
               val params2 = ParameterTool.fromPropertiesFile(parameters.get("file_" + name))
               // Read Parameters from read parameter file
               addParamsFromParamTools(params2)
               i+=1
            }
         }

         //System.out.println("Configuration updated!")

         Parametrization(DISTANCE_THRESHOLD_V, ANGLE_THRESHOLD_V, GAP_PERIOD_V, HISTORY_PERIOD_V, BUFFER_SIZE_V, ANGLE_NOISE_THRESHOLD_V, CLIMB_THRESHOLD_V, CLIMB_NOISE_THRESHOLD_V, SPEED_RATIO_V, NO_SPEED_THRESHOLD_V, LOW_SPEED_THRESHOLD_V, MAX_SPEED_THRESHOLD_V, MAX_RATE_OF_CHANGE_V, MAX_RATE_OF_TURN_V, MAX_ALTITUDE_STOP_V,TYPE_V, AREAS_V)
      }
      catch {
         case nfe: NumberFormatException =>
            throw new RuntimeException("Invalid parametrization", nfe)
      }
   }

  //Apply a configuration from a properties array
  def fromProperties(parameters: Properties): Parametrization = {

      try {

         // Read the list of the ship types (comma separated)
         val types: String = parameters.getProperty("val_SHIP_TYPES")

         emptyArrays() // Empty the arrays holding the default values 
         var i = 0

         if(types == null){
            // If types is null, then the old format is used and we read the params
            // from the current file (they are placed under the name "def_")
            TYPE_V = Map[String,Int]("def_" -> 0)
            addParamsFromProperties(parameters)
         }
         else {
            // Else if the list of ship types is found, for each type there is a param
            // with the location of the file that holds the parameters for said type
            // eg if the type is "ship1" then there is a param with the name "file_ship1"
            // having the location of the new parameter file
            TYPE_V = Map[String,Int]("def_" -> 0)
            types.split(",").foreach{ e =>
               val name = e.trim // Trim starting and ending spaces
               TYPE_V += (name -> i) // Add name to dictionary
               // Open parameter file with the type parameters
               val params2 = ParameterTool.fromPropertiesFile(parameters.getProperty("file_" + name))
               // Read Parameters from read parameter file
               addParamsFromParamTools(params2)
               i+=1
            }
         }

         // Initialize new Areas Instance
         AREAS_V = new Areas()
         
         // Find the location of the areas file
         val areas_file: String = parameters.getProperty("file_AREAS")
         
         if(areas_file != null) {
            // If file is found then initialize areas from file
            AREAS_V = AREAS_V.fromFile(areas_file, 10)

            val area_types: String = parameters.getProperty("val_AREA_TYPES")
            if(area_types == null)
               throw new RuntimeException("Invalid parametrization")

            area_types.split(",").foreach{ e =>
               val name = e.trim // Trim starting and ending spaces
               TYPE_V += (name -> i) // Add name to dictionary
               // Open parameter file with the type parameters
               val params2 = ParameterTool.fromPropertiesFile(parameters.getProperty("file_" + name))
               // Read Parameters from read parameter file
               addParamsFromParamTools(params2)
               i+=1
            }
         }

         //System.out.println("Configuration updated!")

         Parametrization(DISTANCE_THRESHOLD_V, ANGLE_THRESHOLD_V, GAP_PERIOD_V, HISTORY_PERIOD_V, BUFFER_SIZE_V, ANGLE_NOISE_THRESHOLD_V, CLIMB_THRESHOLD_V, CLIMB_NOISE_THRESHOLD_V, SPEED_RATIO_V, NO_SPEED_THRESHOLD_V, LOW_SPEED_THRESHOLD_V, MAX_SPEED_THRESHOLD_V, MAX_RATE_OF_CHANGE_V, MAX_RATE_OF_TURN_V, MAX_ALTITUDE_STOP_V,TYPE_V, AREAS_V)
      }
      catch {
         case nfe: NumberFormatException =>
            throw new RuntimeException("Invalid parametrization", nfe)
      }
   }

     // Methods that return the element of each list that correspond to the name passed as parameter
     def DISTANCE_THRESHOLD(ship_type:String="def_", point:critical_point = null): Double = {
      if(point == null)
         return DISTANCE_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return DISTANCE_THRESHOLD_V(TYPE_V(ship_type))
      
      DISTANCE_THRESHOLD_V(TYPE_V(area_type))
   }
   def ANGLE_THRESHOLD(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return ANGLE_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return ANGLE_THRESHOLD_V(TYPE_V(ship_type))
      
      ANGLE_THRESHOLD_V(TYPE_V(area_type))
   }
   def GAP_PERIOD(ship_type: String = "def_", point: critical_point = null): Long = {
      if(point == null)
         return GAP_PERIOD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return GAP_PERIOD_V(TYPE_V(ship_type))
      
      GAP_PERIOD_V(TYPE_V(area_type))
   }
   def HISTORY_PERIOD(ship_type: String = "def_", point: critical_point = null): Long = {
      if(point == null)
         return HISTORY_PERIOD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return HISTORY_PERIOD_V(TYPE_V(ship_type))
      
      HISTORY_PERIOD_V(TYPE_V(area_type))
   }
   def BUFFER_SIZE(ship_type: String = "def_", point: critical_point = null): Int = {
      if(point == null)
         return BUFFER_SIZE_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return BUFFER_SIZE_V(TYPE_V(ship_type))
      
      BUFFER_SIZE_V(TYPE_V(area_type))
   }
   def ANGLE_NOISE_THRESHOLD(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return ANGLE_NOISE_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return ANGLE_NOISE_THRESHOLD_V(TYPE_V(ship_type))
      
      ANGLE_NOISE_THRESHOLD_V(TYPE_V(area_type))
   }
   def CLIMB_THRESHOLD(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return CLIMB_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return CLIMB_THRESHOLD_V(TYPE_V(ship_type))
      
      CLIMB_THRESHOLD_V(TYPE_V(area_type))
   }
   def CLIMB_NOISE_THRESHOLD(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return CLIMB_NOISE_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return CLIMB_NOISE_THRESHOLD_V(TYPE_V(ship_type))
      
      CLIMB_NOISE_THRESHOLD_V(TYPE_V(area_type))
   }
   def SPEED_RATIO(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return SPEED_RATIO_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return SPEED_RATIO_V(TYPE_V(ship_type))
      
      SPEED_RATIO_V(TYPE_V(area_type))
   }
   def NO_SPEED_THRESHOLD(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return NO_SPEED_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return NO_SPEED_THRESHOLD_V(TYPE_V(ship_type))
      
      NO_SPEED_THRESHOLD_V(TYPE_V(area_type))
   }
   def LOW_SPEED_THRESHOLD(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return LOW_SPEED_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return LOW_SPEED_THRESHOLD_V(TYPE_V(ship_type))
      
      LOW_SPEED_THRESHOLD_V(TYPE_V(area_type))
   }
   def MAX_SPEED_THRESHOLD(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return MAX_SPEED_THRESHOLD_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return MAX_SPEED_THRESHOLD_V(TYPE_V(ship_type))
      
      MAX_SPEED_THRESHOLD_V(TYPE_V(area_type))
   }
   def MAX_RATE_OF_CHANGE(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return MAX_RATE_OF_CHANGE_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return MAX_RATE_OF_CHANGE_V(TYPE_V(ship_type))
      
      MAX_RATE_OF_CHANGE_V(TYPE_V(area_type))
   }
   def MAX_RATE_OF_TURN(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return MAX_RATE_OF_TURN_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return MAX_RATE_OF_TURN_V(TYPE_V(ship_type))
      
      MAX_RATE_OF_TURN_V(TYPE_V(area_type))
   }
   def MAX_ALTITUDE_STOP(ship_type: String = "def_", point: critical_point = null): Double = {
      if(point == null)
         return MAX_ALTITUDE_STOP_V(TYPE_V(ship_type)) 
      
      val x = point.getLongitude
      val y = point.getLatitude
      val area_type: String = AREAS_V.getAreaType(x, y)
      if(area_type == null)
         return MAX_ALTITUDE_STOP_V(TYPE_V(ship_type))
      
      MAX_ALTITUDE_STOP_V(TYPE_V(area_type))
   }

}
