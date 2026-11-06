package sample;

import sample.queueing.Link;
import sample.queueing.QueueingNode;

//
// A source whose jobs are served by a ~QueueingNode before a sink consumes them.
//
network Network
{
    submodules:
        source: Source;
        node: QueueingNode;
        sink: Sink;
    connections:
        source.out --> Link --> node.in;
        node.out --> Link --> sink.in;
}
