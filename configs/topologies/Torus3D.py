# Copyright (c) 2025 Lab Assignment
# 3D Torus topology implementation

from m5.params import *
from m5.objects import *
from common import FileSystemConfig
from topologies.BaseTopology import SimpleTopology


class Torus3D(SimpleTopology):
    description = "Torus3D"

    def __init__(self, controllers):
        self.nodes = controllers

    def makeTopology(self, options, network, IntLink, ExtLink, Router):
        nodes = self.nodes
        num_routers = options.num_cpus

        # Get 3D torus dimensions from command line parameters
        # If not specified, use reasonable defaults
        if hasattr(options, "torus_x") and options.torus_x > 0:
            self.dim_x = options.torus_x
        else:
            self.dim_x = 2  # default

        if hasattr(options, "torus_y") and options.torus_y > 0:
            self.dim_y = options.torus_y
        else:
            self.dim_y = 2  # default

        if hasattr(options, "torus_z") and options.torus_z > 0:
            self.dim_z = options.torus_z
        else:
            self.dim_z = 2  # default

        # Fallback: if the dimensions don't match num_routers,
        # calculate reasonable defaults
        if self.dim_x * self.dim_y * self.dim_z != num_routers:
            # For 64 nodes: 4x4x4, for 16 nodes: 2x2x4, etc.
            if num_routers == 64:
                self.dim_x, self.dim_y, self.dim_z = 4, 4, 4
            elif num_routers == 16:
                self.dim_x, self.dim_y, self.dim_z = 2, 2, 4
            elif num_routers == 8:
                self.dim_x, self.dim_y, self.dim_z = 2, 2, 2
            else:
                # Default to as close to cube as possible
                import math

                cube_root = int(round(num_routers ** (1 / 3)))
                self.dim_x = cube_root
                self.dim_y = cube_root
                self.dim_z = num_routers // (cube_root * cube_root)
                if self.dim_x * self.dim_y * self.dim_z != num_routers:
                    # Fallback to 1D arrangement in Z dimension
                    self.dim_x, self.dim_y, self.dim_z = 1, 1, num_routers

        assert self.dim_x * self.dim_y * self.dim_z == num_routers, (
            f"3D Torus dimensions {self.dim_x}x{self.dim_y}x{self.dim_z} = "
            f"{self.dim_x * self.dim_y * self.dim_z} "
            f"don't match num_routers {num_routers}"
        )

        print(
            f"Creating 3D Torus topology: "
            f"{self.dim_x}x{self.dim_y}x{self.dim_z} = {num_routers} routers"
        )

        link_latency = options.link_latency
        router_latency = options.router_latency

        cntrls_per_router, remainder = divmod(len(nodes), num_routers)
        assert remainder == 0  # For simplicity, assume even distribution

        # Create routers
        routers = [
            Router(router_id=i, latency=router_latency)
            for i in range(num_routers)
        ]
        network.routers = routers

        link_count = 0

        # Connect nodes to routers (external links)
        ext_links = []
        for (i, n) in enumerate(nodes):
            cntrl_level, router_id = divmod(i, num_routers)
            ext_links.append(
                ExtLink(
                    link_id=link_count,
                    ext_node=n,
                    int_node=routers[router_id],
                    latency=link_latency,
                )
            )
            link_count += 1

        network.ext_links = ext_links

        # Create internal links for 3D torus
        int_links = []

        # Helper function to convert 3D coordinates to router ID
        def coord_to_id(x, y, z):
            return z * self.dim_x * self.dim_y + y * self.dim_x + x

        # Create bidirectional links in X dimension (East-West)
        for z in range(self.dim_z):
            for y in range(self.dim_y):
                for x in range(self.dim_x):
                    curr_id = coord_to_id(x, y, z)
                    next_x = (x + 1) % self.dim_x  # Torus wrapping
                    next_id = coord_to_id(next_x, y, z)

                    # East direction link
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[curr_id],
                            dst_node=routers[next_id],
                            src_outport="East",
                            dst_inport="West",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

                    # West direction link (reverse)
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[next_id],
                            dst_node=routers[curr_id],
                            src_outport="West",
                            dst_inport="East",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

        # Create bidirectional links in Y dimension (North-South)
        for z in range(self.dim_z):
            for x in range(self.dim_x):
                for y in range(self.dim_y):
                    curr_id = coord_to_id(x, y, z)
                    next_y = (y + 1) % self.dim_y  # Torus wrapping
                    next_id = coord_to_id(x, next_y, z)

                    # North direction link
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[curr_id],
                            dst_node=routers[next_id],
                            src_outport="North",
                            dst_inport="South",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

                    # South direction link (reverse)
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[next_id],
                            dst_node=routers[curr_id],
                            src_outport="South",
                            dst_inport="North",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

        # Create bidirectional links in Z dimension (Up-Down)
        for y in range(self.dim_y):
            for x in range(self.dim_x):
                for z in range(self.dim_z):
                    curr_id = coord_to_id(x, y, z)
                    next_z = (z + 1) % self.dim_z  # Torus wrapping
                    next_id = coord_to_id(x, y, next_z)

                    # Up direction link
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[curr_id],
                            dst_node=routers[next_id],
                            src_outport="Up",
                            dst_inport="Down",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

                    # Down direction link (reverse)
                    int_links.append(
                        IntLink(
                            link_id=link_count,
                            src_node=routers[next_id],
                            dst_node=routers[curr_id],
                            src_outport="Down",
                            dst_inport="Up",
                            latency=link_latency,
                            weight=1,
                        )
                    )
                    link_count += 1

        network.int_links = int_links

    def registerTopology(self, options):
        for i in range(options.num_cpus):
            FileSystemConfig.register_node(
                [i], MemorySize(options.mem_size) // options.num_cpus, i
            )
