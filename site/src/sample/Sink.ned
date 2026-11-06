package sample;

//
// Consumes jobs and records their lifetime.
//
simple Sink
{
    parameters:
        @class(sample::Sink);
        @display("i=block/sink");
        @signal[lifetime](type=simtime_t);
        @statistic[lifetime](title="job lifetime"; unit=s; record=mean,max,vector);
    gates:
        input in;
}
