namespace sample;

//
// A job created by ~Source and consumed by ~Sink.
//
message Job
{
    int priority;   // higher values are served first
}
