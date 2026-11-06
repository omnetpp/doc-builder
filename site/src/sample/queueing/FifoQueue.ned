package sample.queueing;

//
// Holds the jobs until the server takes them, in the order they arrived.
//
simple FifoQueue
{
    parameters:
        @class(sample::queueing::FifoQueue);
        @display("i=block/queue");
        @signal[length](type=long);
        @statistic[length](title="queue length"; record=timeavg,max,vector; interpolationmode=sample-hold);
        int capacity = default(-1); // the most jobs it holds, -1 for no limit; a job that does not fit is dropped
    gates:
        input in;
        output out;
}
