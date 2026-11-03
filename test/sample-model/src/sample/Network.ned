package sample;

//
// A source connected to a sink.
//
network Network
{
    submodules:
        source: Source;
        sink: Sink;
    connections:
        source.out --> sink.in;
}
