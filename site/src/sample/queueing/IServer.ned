package sample.queueing;

//
// Interface of the servers that a ~QueueingNode can use: a server takes jobs on its input and sends them on
// when it has served them.
//
moduleinterface IServer
{
    gates:
        input in;
        output out;
}
