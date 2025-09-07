./build/NULL/gem5.opt configs/example/garnet_synth_traffic.py \
    --network=garnet --num-cpus=64 --num-dirs=64 \
    --topology=Torus3D --torus-x=4 --torus-y=4 --torus-z=4 \
    --routing-algorithm=4 --synthetic=uniform_random \
    --sim-cycles=1000000 --injectionrate=1 \
    --inj-vnet=2 --adaptive-tie-breaking=x_first \
    --vcs-per-vnet=4 \
    --escape-vcs=1 \
    --distance-coefficient=0.0 \