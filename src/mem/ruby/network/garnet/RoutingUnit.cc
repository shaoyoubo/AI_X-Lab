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


#include "mem/ruby/network/garnet/RoutingUnit.hh"

#include <cmath>

#include "base/cast.hh"
#include "base/compiler.hh"
#include "debug/RubyNetwork.hh"
#include "mem/ruby/network/garnet/InputUnit.hh"
#include "mem/ruby/network/garnet/OutputUnit.hh"
#include "mem/ruby/network/garnet/Router.hh"
#include "mem/ruby/slicc_interface/Message.hh"

namespace gem5
{

namespace ruby
{

namespace garnet
{

RoutingUnit::RoutingUnit(Router *router)
{
    m_router = router;
    m_routing_table.clear();
    m_weight_table.clear();
}

void
RoutingUnit::addRoute(std::vector<NetDest>& routing_table_entry)
{
    if (routing_table_entry.size() > m_routing_table.size()) {
        m_routing_table.resize(routing_table_entry.size());
    }
    for (int v = 0; v < routing_table_entry.size(); v++) {
        m_routing_table[v].push_back(routing_table_entry[v]);
    }
}

void
RoutingUnit::addWeight(int link_weight)
{
    m_weight_table.push_back(link_weight);
}

bool
RoutingUnit::supportsVnet(int vnet, std::vector<int> sVnets)
{
    // If all vnets are supported, return true
    if (sVnets.size() == 0) {
        return true;
    }

    // Find the vnet in the vector, return true
    if (std::find(sVnets.begin(), sVnets.end(), vnet) != sVnets.end()) {
        return true;
    }

    // Not supported vnet
    return false;
}

/*
 * This is the default routing algorithm in garnet.
 * The routing table is populated during topology creation.
 * Routes can be biased via weight assignments in the topology file.
 * Correct weight assignments are critical to provide deadlock avoidance.
 */
int
RoutingUnit::lookupRoutingTable(int vnet, NetDest msg_destination)
{
    // First find all possible output link candidates
    // For ordered vnet, just choose the first
    // (to make sure different packets don't choose different routes)
    // For unordered vnet, randomly choose any of the links
    // To have a strict ordering between links, they should be given
    // different weights in the topology file

    int output_link = -1;
    int min_weight = INFINITE_;
    std::vector<int> output_link_candidates;
    int num_candidates = 0;

    // Identify the minimum weight among the candidate output links
    for (int link = 0; link < m_routing_table[vnet].size(); link++) {
        if (msg_destination.intersectionIsNotEmpty(
            m_routing_table[vnet][link])) {

        if (m_weight_table[link] <= min_weight)
            min_weight = m_weight_table[link];
        }
    }

    // Collect all candidate output links with this minimum weight
    for (int link = 0; link < m_routing_table[vnet].size(); link++) {
        if (msg_destination.intersectionIsNotEmpty(
            m_routing_table[vnet][link])) {

            if (m_weight_table[link] == min_weight) {
                num_candidates++;
                output_link_candidates.push_back(link);
            }
        }
    }

    if (output_link_candidates.size() == 0) {
        fatal("Fatal Error:: No Route exists from this Router.");
        exit(0);
    }

    // Randomly select any candidate output link
    int candidate = 0;
    if (!(m_router->get_net_ptr())->isVNetOrdered(vnet))
        candidate = rand() % num_candidates;

    output_link = output_link_candidates.at(candidate);
    return output_link;
}


void
RoutingUnit::addInDirection(PortDirection inport_dirn, int inport_idx)
{
    m_inports_dirn2idx[inport_dirn] = inport_idx;
    m_inports_idx2dirn[inport_idx]  = inport_dirn;
}

void
RoutingUnit::addOutDirection(PortDirection outport_dirn, int outport_idx)
{
    m_outports_dirn2idx[outport_dirn] = outport_idx;
    m_outports_idx2dirn[outport_idx]  = outport_dirn;
}

// outportCompute() is called by the InputUnit
// It calls the routing table by default.
// A template for adaptive topology-specific routing algorithm
// implementations using port directions rather than a static routing
// table is provided here.

int
RoutingUnit::outportCompute(RouteInfo route, int inport,
                            PortDirection inport_dirn)
{
    int outport = -1;

    if (route.dest_router == m_router->get_id()) {

        // Multiple NIs may be connected to this router,
        // all with output port direction = "Local"
        // Get exact outport id from table
        outport = lookupRoutingTable(route.vnet, route.net_dest);
        return outport;
    }

    // Routing Algorithm set in GarnetNetwork.py
    // Can be over-ridden from command line using --routing-algorithm = 1
    RoutingAlgorithm routing_algorithm =
        (RoutingAlgorithm) m_router->get_net_ptr()->getRoutingAlgorithm();

    switch (routing_algorithm) {
        case TABLE_:  outport =
            lookupRoutingTable(route.vnet, route.net_dest); break;
        case XY_:     outport =
            outportComputeXY(route, inport, inport_dirn); break;
        // any custom algorithm
        case CUSTOM_: outport =
            outportComputeCustom(route, inport, inport_dirn); break;
        case TORUS3D_: outport =
            outportComputeTorus3D(route, inport, inport_dirn); break;
        case TORUS3D_ADAPTIVE_: outport =
            outportComputeTorus3DAdaptive(route, inport, inport_dirn); break;
        default: outport =
            lookupRoutingTable(route.vnet, route.net_dest); break;
    }

    assert(outport != -1);
    return outport;
}

// XY routing implemented using port directions
// Only for reference purpose in a Mesh
// By default Garnet uses the routing table
int
RoutingUnit::outportComputeXY(RouteInfo route,
                              int inport,
                              PortDirection inport_dirn)
{
    PortDirection outport_dirn = "Unknown";

    [[maybe_unused]] int num_rows = m_router->get_net_ptr()->getNumRows();
    int num_cols = m_router->get_net_ptr()->getNumCols();
    assert(num_rows > 0 && num_cols > 0);

    int my_id = m_router->get_id();
    int my_x = my_id % num_cols;
    int my_y = my_id / num_cols;

    int dest_id = route.dest_router;
    int dest_x = dest_id % num_cols;
    int dest_y = dest_id / num_cols;

    int x_hops = abs(dest_x - my_x);
    int y_hops = abs(dest_y - my_y);

    bool x_dirn = (dest_x >= my_x);
    bool y_dirn = (dest_y >= my_y);

    // already checked that in outportCompute() function
    assert(!(x_hops == 0 && y_hops == 0));

    if (x_hops > 0) {
        if (x_dirn) {
            assert(inport_dirn == "Local" || inport_dirn == "West");
            outport_dirn = "East";
        } else {
            assert(inport_dirn == "Local" || inport_dirn == "East");
            outport_dirn = "West";
        }
    } else if (y_hops > 0) {
        if (y_dirn) {
            // "Local" or "South" or "West" or "East"
            assert(inport_dirn != "North");
            outport_dirn = "North";
        } else {
            // "Local" or "North" or "West" or "East"
            assert(inport_dirn != "South");
            outport_dirn = "South";
        }
    } else {
        // x_hops == 0 and y_hops == 0
        // this is not possible
        // already checked that in outportCompute() function
        panic("x_hops == y_hops == 0");
    }

    return m_outports_dirn2idx[outport_dirn];
}

// Template for implementing custom routing algorithm
// using port directions. (Example adaptive)
int
RoutingUnit::outportComputeCustom(RouteInfo route,
                                 int inport,
                                 PortDirection inport_dirn)
{
    panic("%s placeholder executed", __FUNCTION__);
}

// 3D Torus Dimension-Order Routing (DOR) Algorithm
// Routes first in X, then Y, then Z dimension
// Uses shortest path in each dimension considering torus wraparound
int
RoutingUnit::outportComputeTorus3D(RouteInfo route,
                                   int inport,
                                   PortDirection inport_dirn)
{
    PortDirection outport_dirn = "Unknown";

    // Get torus dimensions from network
    GarnetNetwork* garnet_net =
        safe_cast<GarnetNetwork*>(m_router->get_net_ptr());

    // Get dimensions from network parameters
    int dim_x = garnet_net->getTorusX();
    int dim_y = garnet_net->getTorusY();
    int dim_z = garnet_net->getTorusZ();

    // Convert router IDs to 3D coordinates
    int my_id = m_router->get_id();
    int dest_id = route.dest_router;

    // Convert to 3D coordinates
    int my_z = my_id / (dim_x * dim_y);
    int my_remainder = my_id % (dim_x * dim_y);
    int my_y = my_remainder / dim_x;
    int my_x = my_remainder % dim_x;

    int dest_z = dest_id / (dim_x * dim_y);
    int dest_remainder = dest_id % (dim_x * dim_y);
    int dest_y = dest_remainder / dim_x;
    int dest_x = dest_remainder % dim_x;

    // Calculate distance in each dimension considering torus wraparound
    auto torus_distance =
        [](int curr, int dest, int dim_size) -> std::pair<int, bool> {
        int forward_dist = (dest - curr + dim_size) % dim_size;
        int backward_dist = (curr - dest + dim_size) % dim_size;

        if (forward_dist <= backward_dist) {
            return {forward_dist, true};  // true = forward direction
        } else {
            return {backward_dist, false}; // false = backward direction
        }
    };

    auto [x_dist, x_forward] = torus_distance(my_x, dest_x, dim_x);
    auto [y_dist, y_forward] = torus_distance(my_y, dest_y, dim_y);
    auto [z_dist, z_forward] = torus_distance(my_z, dest_z, dim_z);

    // Dimension-Order Routing: route X first, then Y, then Z
    if (x_dist > 0) {
        // Route in X dimension
        if (x_forward) {
            outport_dirn = "East";
        } else {
            outport_dirn = "West";
        }
    } else if (y_dist > 0) {
        // Route in Y dimension
        if (y_forward) {
            outport_dirn = "North";
        } else {
            outport_dirn = "South";
        }
    } else if (z_dist > 0) {
        // Route in Z dimension
        if (z_forward) {
            outport_dirn = "Up";
        } else {
            outport_dirn = "Down";
        }
    } else {
        // Should not reach here as destination check is done in outportCompute
        panic("All dimensions have zero distance in 3D Torus routing");
    }

    // Check if outport direction exists in the map
    if (m_outports_dirn2idx.find(outport_dirn) == m_outports_dirn2idx.end()) {
        panic("3D Torus routing: outport direction %s not found in router %d",
              outport_dirn.c_str(), m_router->get_id());
    }

    return m_outports_dirn2idx[outport_dirn];
}

// 3D Torus Adaptive Routing with Duato-style Escape VC
// Uses escape VCs for deterministic routing and adaptive VCs for
// congestion-aware routing
int
RoutingUnit::outportComputeTorus3DAdaptive(RouteInfo route,
                                          int inport,
                                          PortDirection inport_dirn)
{
    GarnetNetwork* garnet_net =
        safe_cast<GarnetNetwork*>(m_router->get_net_ptr());

    int dim_x = garnet_net->getTorusX();
    int dim_y = garnet_net->getTorusY();
    int dim_z = garnet_net->getTorusZ();

    int my_id = m_router->get_id();
    int dest_id = route.dest_router;

    // Convert to 3D coordinates
    int my_z = my_id / (dim_x * dim_y);
    int my_remainder = my_id % (dim_x * dim_y);
    int my_y = my_remainder / dim_x;
    int my_x = my_remainder % dim_x;

    int dest_z = dest_id / (dim_x * dim_y);
    int dest_remainder = dest_id % (dim_x * dim_y);
    int dest_y = dest_remainder / dim_x;
    int dest_x = dest_remainder % dim_x;

    // Calculate distance in each dimension considering torus wraparound
    auto torus_distance =
        [](int curr, int dest, int dim_size) -> std::pair<int, bool> {
        int forward_dist = (dest - curr + dim_size) % dim_size;
        int backward_dist = (curr - dest + dim_size) % dim_size;

        if (forward_dist <= backward_dist) {
            return {forward_dist, true};  // true = forward direction
        } else {
            return {backward_dist, false}; // false = backward direction
        }
    };

    auto [x_dist, x_forward] = torus_distance(my_x, dest_x, dim_x);
    auto [y_dist, y_forward] = torus_distance(my_y, dest_y, dim_y);
    auto [z_dist, z_forward] = torus_distance(my_z, dest_z, dim_z);

    // Collect all valid minimal paths (directions that make progress)
    std::vector<PortDirection> adaptive_candidates;

    if (x_dist > 0) {
        if (x_forward) {
            adaptive_candidates.push_back("East");
        } else {
            adaptive_candidates.push_back("West");
        }
    }

    if (y_dist > 0) {
        if (y_forward) {
            adaptive_candidates.push_back("North");
        } else {
            adaptive_candidates.push_back("South");
        }
    }

    if (z_dist > 0) {
        if (z_forward) {
            adaptive_candidates.push_back("Up");
        } else {
            adaptive_candidates.push_back("Down");
        }
    }

    // If no progress needed in any dimension, packet should be at destination
    if (adaptive_candidates.empty()) {
        panic("No adaptive candidates in 3D Torus adaptive routing - "
              "should be at destination");
    }

    // Duato-style escape VC mechanism:
    // VC 0 is reserved as escape VC for deterministic dimension-order routing
    // VCs 1+ are adaptive VCs for congestion-aware routing

    // For adaptive routing, check if adaptive VCs (1+) are available
    // If not, fall back to escape VC (0) with deterministic routing

    PortDirection best_direction = "Unknown";
    bool use_escape_vc = false;

    // First, try adaptive routing on available adaptive candidates
    // Check congestion and VC availability for adaptive directions
    int best_score = INT_MAX;
    bool found_adaptive_path = false;

    for (const auto& direction : adaptive_candidates) {
        if (m_outports_dirn2idx.find(direction) == m_outports_dirn2idx.end()) {
            continue;  // Skip if direction not available
        }

        int outport_idx = m_outports_dirn2idx[direction];

        // Check if this outport has available adaptive VCs (VCs 1+)
        // Simple heuristic: assume adaptive VCs are available with some
        // probability. In a real implementation, this would check actual VC
        // states
        bool has_adaptive_vc = checkAdaptiveVCAvailability(outport_idx);

        if (has_adaptive_vc) {
            // Calculate congestion score for this direction
            int congestion_score = getDirectionCongestionScore(outport_idx,
                                                               direction);

            if (congestion_score < best_score) {
                best_score = congestion_score;
                best_direction = direction;
                found_adaptive_path = true;
            }
        }
    }

    // If no adaptive path found, use escape VC with deterministic routing
    if (!found_adaptive_path) {
        use_escape_vc = true;

        // Dimension-Order Routing for escape VC
        if (x_dist > 0) {
            best_direction = x_forward ? "East" : "West";
        } else if (y_dist > 0) {
            best_direction = y_forward ? "North" : "South";
        } else if (z_dist > 0) {
            best_direction = z_forward ? "Up" : "Down";
        }
    }

    // Validate the selected direction
    if (m_outports_dirn2idx.find(best_direction) ==
        m_outports_dirn2idx.end()) {
        panic("3D Torus adaptive routing: selected direction %s not found "
              "in router %d",
              best_direction.c_str(), m_router->get_id());
    }

    return m_outports_dirn2idx[best_direction];
}

// Helper function to check if adaptive VCs are available for an outport
bool
RoutingUnit::checkAdaptiveVCAvailability(int outport_idx)
{
    // Access the router's output unit for this outport
    auto output_unit = m_router->getOutputUnit(outport_idx);

    // Check if adaptive VCs (VC 1 and higher) are available
    // During route computation, we can only check basic availability
    // More sophisticated congestion checking would require runtime state

    int vcs_per_vnet = output_unit->getVcsPerVnet();
    int num_vnets = m_router->get_num_vcs() / vcs_per_vnet;

    // Check each virtual network for potentially available adaptive VCs
    for (int vnet = 0; vnet < num_vnets; vnet++) {
        // For each vnet, check VCs 1+ (adaptive VCs)
        for (int vc_offset = 1; vc_offset < vcs_per_vnet; vc_offset++) {
            int vc_id = vnet * vcs_per_vnet + vc_offset;

            // During route computation, we can only check if VC is idle
            // We can't check credits because VC might not be allocated
            // yet
            if (output_unit->is_vc_idle(vc_id, curTick())) {
                // Found at least one potentially available adaptive VC
                return true;
            }
        }
    }

    return false; // No adaptive VCs appear to be available
}

// Helper function to calculate congestion score for a direction
int
RoutingUnit::getDirectionCongestionScore(int outport_idx,
                                        const PortDirection& direction)
{
    // Get basic congestion information from the output unit
    auto output_unit = m_router->getOutputUnit(outport_idx);

    int vcs_per_vnet = output_unit->getVcsPerVnet();
    int num_vnets = m_router->get_num_vcs() / vcs_per_vnet;

    int congestion_score = 0;
    int idle_vcs = 0;
    int total_adaptive_vcs = 0;

    // Calculate congestion based on idle VC availability
    for (int vnet = 0; vnet < num_vnets; vnet++) {
        // Check adaptive VCs (VCs 1+) for availability
        for (int vc_offset = 1; vc_offset < vcs_per_vnet; vc_offset++) {
            int vc_id = vnet * vcs_per_vnet + vc_offset;
            total_adaptive_vcs++;

            // Count idle VCs (lower congestion)
            if (output_unit->is_vc_idle(vc_id, curTick())) {
                idle_vcs++;
            }
        }
    }

    // Calculate congestion score (lower is better)
    if (total_adaptive_vcs > 0) {
        // More idle VCs = lower congestion score
        congestion_score = total_adaptive_vcs - idle_vcs;
    } else {
        congestion_score = 100; // High congestion if no adaptive VCs
    }

    // Add some randomization for tie-breaking
    congestion_score += rand() % 3;

    return congestion_score;
}

} // namespace garnet
} // namespace ruby
} // namespace gem5
