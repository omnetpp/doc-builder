package sample.queueing;

//
// A queue in front of a server. The server is any module that implements ~IServer.
//
module QueueingNode
{
    parameters:
        string serverType = default("Server"); // the NED type of the server, a module like IServer
        @display("i=block/network2");
    gates:
        input in;
        output out;
    submodules:
        queue: FifoQueue;
        server: <serverType> like IServer;
    connections:
        in --> queue.in;
        queue.out --> server.in;
        server.out --> out;
}
