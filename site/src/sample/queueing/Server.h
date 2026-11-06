#ifndef __SAMPLE_QUEUEING_SERVER_H
#define __SAMPLE_QUEUEING_SERVER_H

#include <omnetpp.h>

using namespace omnetpp;

namespace sample {

/** The modules of a queueing node. */
namespace queueing {

class FifoQueue;

/**
 * Serves one job at a time. A long job takes twice the `serviceTime` parameter.
 *
 * See the NED documentation for parameters and statistics.
 */
class Server : public cSimpleModule
{
  protected:
    cMessage *jobServiced = nullptr;
    cMessage *endServiceMsg = nullptr;
    FifoQueue *queue = nullptr;
    simsignal_t busySignal;

  public:
    virtual ~Server();

    /** Whether the server can take a job now. */
    bool isIdle() const { return jobServiced == nullptr; }

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;

    /** The service time of the job, from its kind and the `serviceTime` parameter. */
    virtual simtime_t getServiceTime(cMessage *job);
};

} // namespace queueing
} // namespace sample

#endif
