# Beer Game: Existing Python Implementations

## Key Implementations

### 1. BPTK (Business Prototyping Toolkit) - transentis
- **URL**: https://github.com/transentis/beergame
- System Dynamics DSL version in `src/sd_dsl/`
- Agent-based version in `src/abm/`
- XMILE/Stella version in `simulation_models/`
- Includes Jupyter notebooks for analysis and AI training
- Stock-flow structure with explicit delay modeling

### 2. DeepBeerInventory-RL (OptMLGroup)
- **URL**: https://github.com/OptMLGroup/DeepBeerInventory-RL
- `BGAgent.py`: Agent class with properties and functionality
- `clBeergame.py`: Instantiates agents and runs simulation
- Uses reinforcement learning (SRDQN) to train optimal agents
- Focus on optimal policy learning rather than behavioral modeling

### 3. SupplyChainSimulation (TomLaMantia)
- **URL**: https://github.com/TomLaMantia/SupplyChainSimulation
- Python simulator illustrating delay loop effects
- Simpler implementation focused on educational use
- Good reference for basic structure

### 4. BeergameAI
- **URL**: https://beergameai.github.io/
- Reinforcement learning approach to playing the beer game
- Focuses on training AI agents to discover optimal policies

## Common Architecture Patterns
1. **Agent class** per echelon (retailer, wholesaler, distributor, factory)
2. **Pipeline/delay queues** for shipping and order processing
3. **Step-based simulation** with explicit ordering of operations
4. **Cost tracking** with holding and backlog costs
5. **Demand generator** with configurable patterns (step, sinusoidal, random)

## Sources
- [GitHub - transentis/beergame](https://github.com/transentis/beergame)
- [GitHub - OptMLGroup/DeepBeerInventory-RL](https://github.com/OptMLGroup/DeepBeerInventory-RL)
- [GitHub - TomLaMantia/SupplyChainSimulation](https://github.com/TomLaMantia/SupplyChainSimulation)
