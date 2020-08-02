-----------------------------------------------------------
Project: datAcron (http://ai-group.ds.unipi.gr/datacron/)
Task: 2.1 Trajectory detection & summarization
Module: Synopses Generator
Version: 0.7. 
Description: Source code for Trajectory detection and summarization built on Apache Flink 0.10.2 (streaming) platform.
Author: Kostas Patroumpas (UPRC)
Created: 21/10/2016
Revised: 10/07/2017
-----------------------------------------------------------

---------------------
SOFTWARE REQUIREMENTS
---------------------

The following software must have been installed prior of executing the source code:

i)   Java SDK ver. 1.8.x  'sudo apt install openjdk-8-jdk'

ii)  Apache Maven ver. 3.0.4 (or higher)

iii)  Apache Flink ver. 0.10.2.


---------------------------------------------------------
Linux installation as carried out on a typical server:
---------------------------------------------------------

Assuming that: 

-- Java installed at /usr/lib/jvm/        -- Java ver. 1.8 was installed

-- Maven installed at /usr/share/maven/   -- Maven ver 3.0.5 currently installed

The following Java-related parameters must be set:

export JAVA_HOME=/usr/lib/jvm/java-8-oracle

export JRE_HOME=/usr/lib/jvm/java-8-oracle/jre 	

export PATH=$PATH:/usr/lib/jvm/java-8-oracle/bin:/usr/lib/jvm/java-8-oracle/jre/bin

export PATH=/usr/share/maven/bin:$PATH

-- Verify that variables are set:

printenv PATH

-------------------------------------------------------------------------

-- JAVA SDK must have been installed. Verify version:

java -version


--MAVEN must have been installed. Run this Linux command to verify its version:

mvn -v


------------------------
Apache FLINK
------------------------

-- Assuming that a local installation of Apache Flink (after just extracting the downloaded .tgz file) is placed in this directory:

cd ~/infore/flink-0.10.2


-- Starting Flink job manager locally: 

bin/start-local.sh


-- Check services actually running:

jps


-- Check the JobManager�s web frontend (Replace <MY_HOST> with the DNS IP address of your localhost): 

http://<MY_HOST>:8081 


-- Stopping Flink job manager:

bin/stop-local.sh


-- To enable more task slots that each TaskManager offers (each slot runs one parallel pipeline), modify Flink configuration in file 'flink-conf.yaml', e.g., by setting:

taskmanager.numberOfTaskSlots: 8


****************************************************************
Controlling Flink jobs
****************************************************************

--List scheduled and running jobs (including their JobIDs):

~/infore/flink-0.10.2/bin/flink list


--List scheduled jobs (including their JobIDs):

~/infore/flink-0.10.2/bin/flink list -s


--List running jobs (including their JobIDs):

~/infore/flink-0.10.2/bin/flink list -r


--List running Flink jobs inside Flink YARN session:

~/infore/flink-0.10.2/bin/flink list -m yarn-cluster -yid <yarnApplicationID> -r


--Cancel a Flink job:

~/infore/flink-0.10.2/bin/flink cancel <jobID>


--Cancel a job with a savepoint:

~/infore/flink-0.10.2/bin/flink cancel -s [targetDirectory] <jobID>


-- View streaming output results from Flink:

tail -f ~/infore/flink-0.10.2/log/flink-*-jobmanager-*.out


************************************************************************
TESTS
************************************************************************

-------------------------------------------------------------
1) Compiling the source code
-------------------------------------------------------------

-- Created a Scala project with a MAVEN archetype as defined in file: pom.xml
-- 'trajectory_synopses' is the name of the directory where source and target code will be stored.

-- Building the project using MAVEN:

cd ~/infore/datacron/implementation/trajectory_synopses/

mvn clean package -Pbuild-jar



-------------------------------------------------
2) CONFIGURATION for executing the compiled code
-------------------------------------------------

-- IMPORTANT! Execution is controlled by a configuration file '*_config.properties'.
-- Such configuration files must always be placed under directory '~/infore/datacron/config/trajectory_synopses/'. Application ALWAYS looks at this path for configuring its execution.

-- Main configurations regarding input, output, and parametrization for each use case:

* aviation_config.properties => Configuration for the AVIATION use case.

* maritime_config.properties => Configuration for the MARITIME use case.

-- CAUTION! Rename your properties file into 'aviation_config.properties' or 'maritime_config.properties' in order to use it for the respective use case without changing the source code.
