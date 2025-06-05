# Summarization data measures

Given these data are stale, calculation of data are time-weighted

# cpu-load

* DevID
* AvgCpuUsage
* MaxCpuUsage
* DataPoints
* TotalDurationSeconds

## DevID

The identification for each node in the experiment

## AvgCpuUsage

Sum(CPU_Load * Time_Gap) / Sum(Time_Gap) or Sum(CPU_Load * Time_Gap) / TotalDuration

*Time_Gap refers to the difference in Timestamp between the current and the next*

## MaxCpuUsage

Max(CPU_Load)

## DataPoints

Amount of datapoints the summery relies on

## TotalDuration

Time from the earliest timestamp to the latest

# file

* DevID
* TotalFilesChanged
* AvgFilesChangedPerMin
* PeakFilesChangedPerMin
* ChangeTimeSpanMinutes

## DevID

The identification for each node in the experiment

## TotalFilesChanged

The count of file changes recorded in the data

## AvgFilesChangedPerMin

TotalFilesChanged / (Duration_In_Seconds / 60)

## PeakFilesChangedPerMin

The max of file changes count, when grouped by minutes

## ChangeTimeSpanMinutes

The Timestamp difference between the first change and the last change.

*Notice that the baseline commit does not count*


# network

* IP_A
* IP_B
* TotalPackets
* TotalBytes
* TotalActiveSeconds
* AvgRateMbps
* PeakRateMbps

## IP_A and IP_B

The two ends of the communication

## TotalPackets

Sum of the packet count between the two hosts

## TotalBytes

Sum of the packet size in bytes count between the two hosts

## TotalActiveSeconds

The difference in Timestamp between the first and last packet between the two hosts

## AvgRateMbps

TotalBytes / TotalActiveSeconds

## PeakRateMbps

The max of sum of packet size, when grouped by seconds


# proc-cpu

*Notice that proc-cpu does not capture all processes, it only capture the top ones*

* Name
* Duration
* AvgCpuPercent
* MaxCpuUsage
* DataPoints

## Name

The name of the process

## Duration

The Sum of Time_Gap when the process appears in records

*Time_Gap refers to the difference in Timestamp between the current and the next*

## AvgCpuPercent

Sum(CPU_Usage * Time_Gap) / Duration

## MaxCpuUsage

Max of CPU_Usage of the process

## DataPoints

Count of datapoints containing the coresponding process


# proc-mem

* Name
* TimeWeightedAvgVmSizeMiB
* MaxVmPeakMiB
* MaxVmHwmMiB 
* DataPoints
* PeakDuration

## Name

The name of the process

## TimeWeightedAvgVmSizeMiB

Sum(VmSize * Time_Gap) / (Peak)Duration

## (Peak)Duration

The timestamp difference between the current and the next, for the coresponding process

## MaxVmPeakMiB

The max of VmPeak for the coresponding process

## MaxVmHwmMiB

The max of VmHwm for the coresponding process

## DataPoints

The count of datapoints that contains the coresponding process


# proc-new

* DevID
* TotalNewProcs
* AvgNewProcsPer30Sec
* PeakNewProcsPer30Sec
* TotalTime

## DevID

The identification for each node in the experiment

## TotalNewProcs

Count of datapoints in the records

## AvgNewProcsPer30Sec

TotalNewProcs / TotalTime


## PeakNewProcsPer30Sec

The max of new process count, when grouped by 30 seconds

## TotalTime

The difference between the earlist Timestamp and the latest Timestamp in the record
