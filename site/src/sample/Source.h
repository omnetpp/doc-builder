#ifndef __SAMPLE_SOURCE_H
#define __SAMPLE_SOURCE_H

#include <omnetpp.h>

using namespace omnetpp;

namespace sample {

/**
 * Generates jobs at intervals given by the `interval` parameter.
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
