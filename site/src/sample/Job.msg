namespace sample;

//
// What a job asks of the server.
//
enum JobKind
{
    JOB_SHORT = 0;   // served in the base service time
    JOB_LONG = 1;    // takes twice as long
}

//
// A job created by ~Source, served by a ~QueueingNode, and consumed by ~Sink.
//
message Job
{
    JobKind kind = JOB_SHORT;
    int priority;               // higher values are served first
    simtime_t queueingTime;     // the time the job spent waiting in queues
}
