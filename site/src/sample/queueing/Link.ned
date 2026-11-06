package sample.queueing;

//
// The connection between two modules of the network: a job takes the time of its delay to cross it.
//
channel Link extends ned.DelayChannel
{
    delay = default(10ms);
}
