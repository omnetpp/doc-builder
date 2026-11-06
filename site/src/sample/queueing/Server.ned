package sample.queueing;

//
// Serves one job at a time, each for its service time, and asks its queue for the next one when it is idle.
//
simple Server like IServer
{
    parameters:
        @class(sample::queueing::Server);
        @display("i=block/server");
        @signal[busy](type=bool);
        @statistic[busy](title="server busy"; record=timeavg,vector; interpolationmode=sample-hold);
        volatile double serviceTime @unit(s) = default(exponential(0.5s)); // service time of a short job
    gates:
        input in;
        output out;
}
