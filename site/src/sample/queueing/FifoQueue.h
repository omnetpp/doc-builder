#ifndef __SAMPLE_QUEUEING_FIFOQUEUE_H
#define __SAMPLE_QUEUEING_FIFOQUEUE_H

#include <omnetpp.h>

using namespace omnetpp;

namespace sample {
namespace queueing {

/**
 * Holds the jobs in arrival order until the Server asks for the next one.
 *
 * See the NED documentation for parameters and statistics.
 */
class FifoQueue : public cSimpleModule
{
  protected:
    cQueue queue;
    int capacity = -1;
    simsignal_t lengthSignal;

  public:
    /** The number of jobs waiting. */
    int getLength() const { return queue.getLength(); }

    /** Sends the first job to the server; the server calls it when it becomes idle. */
    virtual void requestJob();

  protected:
    virtual void initialize() override;

    /** Sends the job to the server if it is idle, and queues it otherwise. */
    virtual void handleMessage(cMessage *msg) override;
};

} // namespace queueing
} // namespace sample

#endif
