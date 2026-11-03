#ifndef __SAMPLE_SINK_H
#define __SAMPLE_SINK_H

#include <omnetpp.h>

using namespace omnetpp;

namespace sample {

/**
 * Consumes jobs and emits their lifetime.
 */
class Sink : public cSimpleModule
{
  protected:
    simsignal_t lifetimeSignal;

  protected:
    virtual void initialize() override;

    /** Records the lifetime of the job and deletes it. */
    virtual void handleMessage(cMessage *msg) override;
};

} // namespace sample

#endif
