#ifndef _PixelAMC13Controller_h_
#define _PixelAMC13Controller_h_

#include "xdaq/Application.h"
#include "xdaq/ApplicationContext.h"
#include "xdaq/ApplicationStub.h"
#include "xdaq/exception/Exception.h"

#include "xdaq/NamespaceURI.h"

#include "xoap/MessageReference.h"
#include "xoap/MessageFactory.h"
#include "xoap/SOAPEnvelope.h"
#include "xoap/SOAPBody.h"
#include "xoap/Method.h"

#include "xdata/Boolean.h"
#include "xdata/UnsignedInteger.h"
#include "xdata/String.h"

#include "PixelUtilities/PixeluTCAUtilities/include/PixelAMC13Interface.h"

class PixelAMC13Controller : public xdaq::Application {
 public:
  XDAQ_INSTANTIATOR();

  xdata::String uri1;
  xdata::String uri2;
  xdata::String addressT1;
  xdata::String addressT2;
  xdata::String mask;
  xdata::UnsignedInteger calBX;

  PixelAMC13Controller(xdaq::ApplicationStub * s) throw (xdaq::exception::Exception);
  ~PixelAMC13Controller() { delete amc13; }

  xoap::MessageReference Reset(xoap::MessageReference msg) throw (xoap::exception::Exception);
  xoap::MessageReference Configuration(xoap::MessageReference msg) throw (xoap::exception::Exception);
  xoap::MessageReference Configure(xoap::MessageReference msg) throw (xoap::exception::Exception);
  xoap::MessageReference userCommand(xoap::MessageReference msg) throw (xoap::exception::Exception);
  xoap::MessageReference Enable(xoap::MessageReference msg) throw (xoap::exception::Exception);
  xoap::MessageReference Stop(xoap::MessageReference msg) throw (xoap::exception::Exception);
  xoap::MessageReference Suspend(xoap::MessageReference msg) throw (xoap::exception::Exception);

 private:
  PixelAMC13Interface* amc13;
};

#endif
