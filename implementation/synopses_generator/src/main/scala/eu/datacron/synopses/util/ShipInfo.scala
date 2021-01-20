/******************************************************************************
  * Project: datAcron
  * File: eu.datacron.synopses.util/ShipInfo.scala
  * Description: Holds information for each ship id.
  * Developer: Kostas Patroumpas (UPRC)
  * Date: 17/8/2019
  * Revised: 17/8/2019
  ************************************************************************/

package eu.datacron.synopses

import scala.io.Source

case class ShipInfo(
      var TYPE: Map[String, String]          // Map from Ship ID to Ship Type
   )                      
{


  //Constructor
  def this() {
    this(Map())        //DEFAULT values
  }


  //Print out current properties
  override def toString: String = {
    val sb: StringBuilder = new StringBuilder
    sb.append(TYPE.toString)
    sb.toString()
  }


  def getType(id: String): String = {
    if(TYPE.contains(id)){
      return TYPE(id)
    }
    else
      return "def_"
  }


  // Read a configuration from settings stored in a properties file
  def fromFile(propertiesFile: String): ShipInfo = {
    
    TYPE = Source.fromFile(propertiesFile)
    .getLines
    .toArray
    .map(_.split(" "))
    .map({ x => (x(0),x(1)) }) // First is the ID, next is the ship Type
    .toMap

    ShipInfo(TYPE) // Initialize instance
  }

}
