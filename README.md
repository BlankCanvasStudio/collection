# Discern Data Collection 

The function of this repository is to run experiments in the sphere testbed and collect data from 
the Data Sorcerers on these experiments. 

If you'd like to see a detailed view of the data collection process, see the 
[Instrumentation Repo](https://gitlab.com/mergetb/tech/instrumentation). That repo is for 
maintainers of the instrumentation software and shouldn't be of any concern to most people using 
this package. If you'd like to see how the data is saved to the database and what information is 
stored, please refer to the 
[data documentation in the Instrumentation Repo](https://gitlab.com/mergetb/tech/instrumentation/-/tree/main/docs/data/format?ref_type=heads)


## Quick Start

All the collection code in this repository is meant to be called from the project root and is meant to be run
on an XDC. An analysis code should be executed from the root directory on the users local machine. 

To start an experiment, you should run:

```
./startexp -xs <name>
```

in the root of this repository. 

2 files are needed to implement a new experiment: `models/<exp name>.model` and 
`experiments/<exp name>`.


`models/<exp name>.model` is the topology for your experiment and **NEEDS** to contain a node 
named `fusioncore`, which has a link connecting it to every node you'd like to record data from in
your topology. All the data sensors are hard coded to save their data to a node with this name.

`experiments/<exp name>` is an executable which orchestrates the experiment from the xdc. You 
don't need to run anything related to the sensors in this file, just the experiment you'd like to 
record. All the data collection is handled by `startexp`.

`startexp` handles installing the sensors, building the fusion core, starting everything, and 
exfiltrating the data. 

Once `experiments/<exp name>` has exited, `startexp` will automatically save the data from the 
fusioncore to `~/postgres-data.sql` and `~/influx-data.tar.gz` in your xdc. If you need to take 
more than one point of data, its up to you to properly manage these files.

If you'd like to analyze your data after an experiment, run:

```
./util/setup-databases.sh <path to data folder>
```

on any machine that has docker and the data downloaded. This file will set up the databases to the 
snapshots contained at `<path to data folder>/postgres-data.sql` and 
`<path to data folder>/influx-data.tar.gz` (the output files from `startexp`).

The influx database is accessible at `10.10.10.4:8086` and the postgres database is accessible at 
`10.10.10.3:5432` on the machine `./util/setup-databases.sh` was run on. The scripts in `analyze` 
are already set up to do basic data manipulations on these containers, so `./analyze/*` are set 
to work out of the box. Feel free to modify and extend these scripts as you see fit.

That should be everything you need to know! The rest of this document is technical details on the
software included in this repo, in case you'd only like to use parts of it


### Orchestration

If you have access to a bash command line, needing to orchestrate everything in the XDC is 
tedious. So I've developed the orchestration folder, which will facilitate recording and saving 
data from your local machine (assuming you have mrg and an XDC set up)

The basic command format is:

```
./orchestration/run <xdc> <iterations> <data_location> <experiment name>
```

This will install the collections package, run `startexp -sx <experiment name>`, save the output data 
of the FusionCore to <data_location> on the local machine, and loop this <iteration> times, so you
can easily take data of repeated trials.

So you should only need to run 
`./orchestration/run <xdc> <iterations> <data_location> <experiment & args for startexp>` on your local machine 
and the script will manage everything for you.

Heres a sample command:

```
./orchestration/run sunsh 1 ./data/testing2 -s synflood
```



## Running Step by Step

If you'd like more fine grained controll over the execution process:

```
./startexp <name>
```

will simply create the materialization and install the fusioncore and datasorcerers on that 
materialization. This does require the file `./models/<name>.model`

```
runlab <name>
```

will install the packages for that lab on the topology. No extra files are required for this.

These two steps can be combined into one step with:

```
./startexp -s <name>
```

but this has the added advantage all the commands executed in `runlab` will be excluded from the dataset. 

For a list of all the available experiments, visit: https://jelenamirkovic.github.io/sphere-education.github.io/

Then you can mess with your experiment however you see fit.

To run an experiment script, simply execute:

```
./experiments/<name>
```

The steps above can be automated into one command with:

```
./startlab -xs <name>
```

To save the data once you're done, run:

```
./util/download/databases.sh fusioncore
```

This will create `~/postgres-data.sql` and `~/influx-data.tar.gz` on the xdc, which are database 
snapshots that `./util/setup-databases.sh` can use to let users easily do post hoc analysis.

The first (and only) argument to `./util/setup-databases.sh` is a folder which contains 
`postgres-data.sql` and `influx-data.tar.gz`. This script will stand up docker containers on your 
local machine which contain the data in these snapshots. The files in `analysis` are currently set 
up to read from these containers.


## What All the Files Do

`install` contains the scripts which install the data sorcerers and fusion core into the topology

`./install/core.sh <node>` can be used to install the fusion core on a specific node. But you'll 
need to alter the configs on all the nodes running the Data Sorcerers. To see details on all the 
configuration options please see the [configuration documentation in the Instrumentation repo](https://gitlab.com/mergetb/tech/instrumentation/-/tree/main/docs/conf?ref_type=heads).

`./install/sensors.sh` installs the Data Sorcerers on every node in your topology that isn't the 
fusioncore. 

`./install/sensors.sh node1 node2` only installs the Sorcerers on node1 and node2.

`./util/download/databases.sh <fusion core node>` downloads a snap shot of the databases in the 
<fusion core node> to `~/postgres-data.sql` and `~/influx-data.tar.gz` in an xdc.

`./analyze/*` show examples of data manipulation post hoc.



