package sample;

//
// Generates jobs at random intervals and sends them to its output.
//
// See ~Sink for the module that consumes them.
//
simple Source
{
    parameters:
        @class(sample::Source);
        @display("i=block/source");
        @signal[created](type=long);
        @statistic[created](title="jobs created"; record=count,vector);
        volatile double interval @unit(s) = default(exponential(1s)); // time between two jobs
        string jobName = default("job");
    gates:
        output out;
}
