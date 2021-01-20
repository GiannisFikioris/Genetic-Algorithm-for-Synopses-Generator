-----------------------------------------------------------------------------------------------------
-- Object : AIS Dynamic Data (version 2)
-- File name : nari_dynamic.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v2 (31/05/2017)
-- SRID : WGS84 
-- Coverage : Longitude between -10.00 and 0.00 and Latitude between 45.00 and 51.00
-- Volume : 18.648.556 decoded dynamic messages
-- Period : 6 months (2015-10-01 00:00:00 UTC to 2016-03-31 23:59:59 UTC)
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains AIS Dynamic Data collected by Naval Academy receiver. The file combines message types ITU 1, ITU 2, ITU 3, ITU 18, ITU 19. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute	Data type		Description
-----------------------------------------------------------------------------------------------------
*  mmsi 	integer           	MMSI identifier for vessel
*  status 	integer          	Navigational status
*  turn 	double precision  	Rate of turn, right or left, 0 to 720 degrees per minute
*  speed 	double precision 	Speed over ground in knots (allowed values: 0-102.2 knots)
*  course 	double precision  	Course over ground (allowed values: 0-359.9 degrees)
*  heading 	integer      		True heading in degrees (0-359), relative to true north
*  lon 		double precision  	Longitude (georeference: WGS 1984)
*  lat 		double precision 	Latitude  (georeference: WGS 1984)
*  t 		bigint              timestamp in UNIX epochs

** Status linked to "Navigational Status.csv"


-----------------------------------------------------------------------------------------------------
-- Object : AIS Dynamic Data (version 2)
-- File name : nari_dynamic_aton.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v2 (31/05/2017)
-- SRID : WGS84 
-- Coverage : Longitude between -10.00 and 0.00 and Latitude between 45.00 and 51.00
-- Volume : 499.194 decoded dynamic messages
-- Period : 6 months (2015-10-01 00:00:00 UTC to 2016-03-31 23:59:59 UTC)
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains AIS Dynamic Data collected by Naval Academy receiver. The file combines message type ITU 21. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute	Data type		Description
-----------------------------------------------------------------------------------------------------
*  mmsi 	  integer             MMSI identifier of the SAR aircraft
*  typeofaid  smallint			  0 = not available = default; refer to appropriate definition set up by IALA otherwise
*  aidsname   text 				  The name of the AtoN (max 20 characters)
*  virtual    boolean             0 = default = real AtoN at indicated position; 1 = virtual AtoN, does not physically exist 	
*  lon 		  double precision    Longitude (georeference: WGS 1984)
*  lat 		  double precision 	  Latitude  (georeference: WGS 1984)
*  t 		  bigint              timestamp in UNIX epochs

** refer ATON.csv for typeofaid description

-----------------------------------------------------------------------------------------------------
-- Object : AIS Dynamic Data (version 2)
-- File name : nari_dynamic_sar.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v2 (31/05/2017)
-- SRID : WGS84 
-- Coverage : Longitude between -10.00 and 0.00 and Latitude between 45.00 and 51.00
-- Volume : 4.446 decoded dynamic messages
-- Period : 6 months (2015-10-01 00:00:00 UTC to 2016-03-31 23:59:59 UTC)
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains AIS Dynamic Data collected by Naval Academy receiver. The file combines message type ITU 9. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute	Data type		Description
-----------------------------------------------------------------------------------------------------
*  mmsi 	integer           	MMSI identifier of the SAR aircraft
*  altitude smallint			Altitude of the search and rescue aircraft (0-4094 m)
*  speed 	double precision 	Speed over ground in knots (allowed values: 0-1022 knots)
*  course 	double precision  	Course over ground (allowed values: 0-359.9 degrees)
*  lon 		double precision  	Longitude (georeference: WGS 1984)
*  lat 		double precision 	Latitude  (georeference: WGS 1984)
*  t 		bigint              timestamp in UNIX epochs


-----------------------------------------------------------------------------------------------------
-- Object : AIS Static Data (version 2)
-- File name : nari_ais_static.csv
-- Source : Naval Academy, France (ecole-navale.fr)
-- Dataset version : v2 (31/05/2017)
-- SRID : NA 
-- Coverage : Longitude between -10.00 and 0.00 and Latitude between 45.00 and 51.00
-- Volume : 1.032.187 decoded static messages
-- Period : 6 months (2015-10-01 00:00:00 UTC to 2016-03-31 23:59:59 UTC)
-- Licence : CC-BY-NC-SA-4.0
-- Description : The csv file constains static and voyage-related information collected by Naval Academy receiver. The file combines message types ITU 5, ITU 19, ITU 24. The following describes fields included in the file.
-----------------------------------------------------------------------------------------------------
Attribute	Data type		Description
-----------------------------------------------------------------------------------------------------
*  sourcemmsi 	  integer         	MMSI identifier for vessel
*  imo 			  integer         	IMO ship identification number (7 digits); 
*  callsign 	  text            	International radio call sign (max 7 characters), assigned to the vessel by its country of registry
*  shipname 	  text            	Name of the vessel (max 20 characters)
*  shiptype 	  integer           Code for the type of the vessel (see enumeration)
*  to_bow 	  	  integer          	Distance (meters) to Bow
*  to_stern 	  integer         	Distance (meters) to Stern --> to_bow + to_stern = LENGTH of the vessel
*  to_starboard   integer      		Distance (meters) to Starboard, i.e., right side of the vessel --> to_port + to_starboard = BEAM at the vessel's nominal waterline
*  to_port 		  integer           Distance (meters) to Port, i.e., left side of the vessel (meters)  
*  eta 			  text            	ETA (estimated time of arrival) in format dd-mm hh:mm (day, month, hour, minute) – UTC time zone
*  draught 		  double precision  Allowed values: 0.1-25.5 meters
*  destination 	  text            	Destination of this trip (manually entered)
*  mothershipmmsi integer			Dimensions of ship in metres and reference point for reported position
*  t 			  bigint          	timestamp in UNIX epochs

** shiptype linked to the range shiptype_min to shiptype_max in "Ship Types List.csv"
** country name can be obtained through MMSI prefix which is linked to "MMSI Country Codes.csv"
*** callsign can be linked with IRCS in EU fleet register (EuropeanVesselRegister.csv )
