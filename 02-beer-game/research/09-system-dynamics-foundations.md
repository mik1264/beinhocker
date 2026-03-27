# System Dynamics and Supply Chain: Forrester's Foundations

## Historical Context
- Jay W. Forrester published the first system dynamics paper in **1958**
- The field was initially called **Industrial Dynamics**
- Based on a hydraulic metaphor: flow of water into and out of reservoirs
- Published in book form: *Industrial Dynamics* (1961)

## The Forrester Model
A production-distribution system described in terms of **6 interacting flow systems**:
1. **Information flows**: Orders, demand signals, forecasts
2. **Material flows**: Physical goods movement
3. **Order flows**: Purchase orders between echelons
4. **Money flows**: Payments and financial signals
5. **Labor flows**: Workforce allocation
6. **Capital flows**: Equipment and capacity investment

## Stock and Flow Fundamentals

### Stocks (Levels)
- Accumulations that characterize the state of the system
- Examples: inventory, backlog, orders in pipeline, production capacity
- Changed only by flows (inflows increase, outflows decrease)

### Flows (Rates)
- Activities that change stocks over time
- Examples: shipment rate, order rate, production rate
- Controlled by decision rules that depend on system state

### Key Principle
```
Stock(t) = Stock(t-1) + (Inflow - Outflow) · dt
```

## Forrester's Key Insight
Despite the simplicity of a linear supply chain, his model revealed:
- **Persistent oscillations** of production and sales
- Amplification of demand signals upstream
- Counterintuitive behavior arising from delays and feedback
- Policy resistance: seemingly rational interventions making things worse

## Integrated Aspects
Forrester integrated aspects of operations that had not previously been considered:
- Limited information flow across organizations
- Delays in gathering information and making decisions
- Delays in implementation and impact of decisions
- Nonlinear constraints (can't ship negative amounts, capacity limits)

## Legacy
- Foundation for modern supply chain management theory
- Beer Distribution Game as primary pedagogical tool
- Influenced Lee, Padmanabhan & Whang's bullwhip effect research
- System dynamics methodology now applied across domains

## Sources
- [System Dynamics - Wikipedia](https://en.wikipedia.org/wiki/System_dynamics)
- [System Dynamics Modelling in Supply Chain Management](https://informs-sim.org/wsc00papers/049.PDF)
- [Transentis - Stock and Flow Diagrams](https://www.transentis.com/page/stock-and-flow-diagrams)
