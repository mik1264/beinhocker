# Network Rewiring, Preferential Attachment, and Evolving Topology

## Preferential Attachment (Barabási-Albert)
- "Rich get richer" mechanism in network growth
- New nodes preferentially connect to highly connected nodes
- Produces scale-free networks with power-law degree distributions

## Adaptive Rewiring
- Network structure adapts to use patterns
- Short-cuts created where diffusion is intensive
- Underused connections annihilated
- Small-world networks always emerge from random networks through adaptive rewiring

## Evolving Fixed-Size Networks
- In fixed-size networks, topology evolves while node/edge count conserved
- Eventually reaches macroscopically stationary state
- Degree distribution characterizes the stationary topology
- Relevant to Jain-Krishna model where species count is fixed

## Implementation Approach
- Use directed weighted graph with fixed number of nodes
- New species get random connections (like random rewiring)
- Selection pressure (removing least fit) drives topology evolution
- Monitor degree distribution, clustering, path lengths over time

## Sources
- Barabási & Albert, "Emergence of Scaling in Random Networks" (Science, 1999)
- Self-organisation of small-world networks by adaptive rewiring (Scientific Reports, 2017)
