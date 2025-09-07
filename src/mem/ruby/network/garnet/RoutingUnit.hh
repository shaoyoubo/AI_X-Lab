/*
 * Copyright (c) 2008 Princeton University
 * Copyright (c) 2016 Georgia Institute of Technology
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are
 * met: redistributions of source code must retain the above copyright
 * notice, this list of conditions and the following disclaimer;
 * redistributions in binary form must reproduce the above copyright
 * notice, this list of conditions and the following disclaimer in the
 * documentation and/or other materials provided with the distribution;
 * neither the name of the copyright holders nor the names of its
 * contributors may be used to endorse or promote products derived from
 * this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 * OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */


#ifndef __MEM_RUBY_NETWORK_GARNET_0_ROUTINGUNIT_HH__
#define __MEM_RUBY_NETWORK_GARNET_0_ROUTINGUNIT_HH__

#include "mem/ruby/common/Consumer.hh"
#include "mem/ruby/common/NetDest.hh"
#include "mem/ruby/network/garnet/CommonTypes.hh"
#include "mem/ruby/network/garnet/GarnetNetwork.hh"
#include "mem/ruby/network/garnet/flit.hh"

namespace gem5
{

namespace ruby
{

namespace garnet
{

class InputUnit;
class Router;

class RoutingUnit
{
  public:
    RoutingUnit(Router *router);
    int outportCompute(RouteInfo route,
                      int inport,
                      PortDirection inport_dirn,
                      flit* t_flit);

    // Topology-agnostic Routing Table based routing (default)
    void addRoute(std::vector<NetDest>& routing_table_entry);
    void addWeight(int link_weight);

    // get output port from routing table
    int  lookupRoutingTable(int vnet, NetDest net_dest);

    // Topology-specific direction based routing
    void addInDirection(PortDirection inport_dirn, int inport);
    void addOutDirection(PortDirection outport_dirn, int outport);

    // Routing for Mesh
    int outportComputeXY(RouteInfo route,
                         int inport,
                         PortDirection inport_dirn);

    // Custom Routing Algorithm using Port Directions
    int outportComputeCustom(RouteInfo route,
                             int inport,
                             PortDirection inport_dirn);

    // Routing for 3D Torus (Dimension-Order Routing)
    int outportComputeTorus3D(RouteInfo route,
                              int inport,
                              PortDirection inport_dirn);

    // Adaptive Routing for 3D Torus with Duato-style Escape VC
    int outportComputeTorus3DAdaptive(RouteInfo route,
                                     int inport,
                                     PortDirection inport_dirn,
                                     flit* t_flit);

    // Helper functions for adaptive routing
    bool checkAdaptiveVCAvailability(int outport_idx);
    // New function for virtual-network-specific VC availability check
    bool checkAdaptiveVCAvailabilityForVnet(int outport_idx, int vnet);
    int getDirectionCongestionScore(int outport_idx,
                                    const PortDirection& direction);
    // New function for packet-type-specific congestion scoring
    int getDirectionCongestionScoreForVnet(int outport_idx,
                                           const PortDirection& direction,
                                           int vnet);
                                           
    // Distance-aware routing functions
    int calculateRemainingHops(const PortDirection& direction, int dest_ni);
    float calculateDistanceScore(const PortDirection& direction, int dest_ni);
    float calculateCombinedScore(int outport_idx, const PortDirection& direction, 
                                int vnet, int dest_ni);    // Returns true if vnet is present in the vector
    // of vnets or if the vector supports all vnets.
    bool supportsVnet(int vnet, std::vector<int> sVnets);

    // Apply tie-breaking strategy for adaptive routing
    PortDirection applyTieBreakingStrategy(const std::vector<PortDirection>& tie_candidates,
                                          const std::string& strategy,
                                          const std::vector<PortDirection>& all_candidates);

    // Escape VC routing function (mesh-style, no wrap-around)
    PortDirection computeEscapeVCDirection(int my_x, int my_y, int my_z,
                                          int dest_x, int dest_y, int dest_z,
                                          int dim_x, int dim_y, int dim_z);


  private:
    Router *m_router;

    // Routing Table
    std::vector<std::vector<NetDest>> m_routing_table;
    std::vector<int> m_weight_table;

    // Inport and Outport direction to idx maps
    std::map<PortDirection, int> m_inports_dirn2idx;
    std::map<int, PortDirection> m_inports_idx2dirn;
    std::map<int, PortDirection> m_outports_idx2dirn;
    std::map<PortDirection, int> m_outports_dirn2idx;
};

} // namespace garnet
} // namespace ruby
} // namespace gem5

#endif // __MEM_RUBY_NETWORK_GARNET_0_ROUTINGUNIT_HH__
