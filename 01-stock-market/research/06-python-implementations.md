# Python Implementations of SFI ASM

## Key Existing Implementations

### 1. glibor/ArtificialStockMarket-SantaFe
- Files: Agents.py, Market.py, Simulation.py, main.py
- 64-bit watch lists with ternary values [0, 1, 2] (2 = don't care)
- Weight distribution [1, 1, 18] favoring wildcards
- Alpha parameter [0.7, 1.2], Beta parameter [-10, 19]
- GA triggered every 10 steps (configurable)
- Specialist implements clearing and auction pricing

### 2. felixschmitz/ArtificialStockMarketReproduction
- Uses AgentPy framework (ap.Model, ap.Agent)
- ArtificialStockMarket class + MarketStatistician agents
- AR(1) dividend process with configurable mean
- Standard lifecycle: setup() -> step() -> document() -> update()

### 3. aaron-wheeler/SFIArtificialStockMarket.jl (Julia)
- Based on Arthur et al. (1996) and Ehrentreich (2007)
- Full documentation available

## Frameworks Available
- Mesa: Modular ABM framework with visualization
- AgentPy: Integrates design, simulation, and analysis
- abcEconomics: Stock-flow consistent economic simulations

## Common Parameters Across Implementations
- Initial price: ~80-100
- Initial dividend: 10
- Interest rate: 0.10
- Risk aversion (lambda): 0.50
- Rules per agent: ~100
- Dividend AR(1) persistence: 0.95
- Dividend error variance: ~0.0743
