#ifndef __SAMPLE_SOURCE_H
#define __SAMPLE_SOURCE_H

#include <omnetpp.h>

using namespace omnetpp;

/** The sample model: a source of jobs, a queueing node that serves them, and a sink. */
namespace sample {

/**
 * Generates jobs at intervals given by the `interval` parameter, of the kind and priority that it draws for each.
 *
 * See the NED documentation for parameters and statistics.
 */
class Source : public cSimpleModule
{
  protected:
    cMessage *timer = nullptr;
    simsignal_t createdSignal;
    long count = 0;

  public:
    virtual ~Source();

  protected:
    virtual void initialize() override;

    /** Sends a new job and schedules the next one. */
    virtual void handleMessage(cMessage *msg) override;
};

} // namespace sample

#endif
