# Beer Game: Mathematical Model and Equations

## Complete Mathematical Formulation
Based on Sterman (1989) and the JASSS mathematical model paper.

## Parameters and Initial Values

### Delay Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| mdt (mailing delay) | 1 week | Order transmission delay |
| st (shipping time) | 2 weeks | Physical shipping delay |
| plt (production lead time) | 2 weeks | Factory production delay |
| sat (stock adjustment time) | 1 week | Adjustment speed |

### Cost Parameters
| Parameter | Value | Description |
|-----------|-------|-------------|
| uihc (holding cost) | $0.50/case/week | Inventory holding cost |
| ubc (backlog cost) | $1.00/case/week | Backlog penalty cost |

### Initial Conditions
| Variable | Value |
|----------|-------|
| Initial inventory (all) | 12 cases |
| Initial backlog (all) | 0 cases |
| Initial in-transit (each stage) | 4 cases |
| Initial demand/orders | 4 cases/week |

## Step-by-Step Simulation Logic

### Step 1: Receive Inventory and Advance Shipping Delays
```
I_i,t = I_i,t-1 + ITI2_i,t-1
ITI2_i,t = ITI1_i,t-1
ITI1_i,t = 0
```
(Factory uses WIP stages instead of ITI)

### Step 2: Fill Orders (Shipments)
```
S_i,t = min(I_i,t, B_i,t + IO_i,t)
ITI1_downstream,t = S_i,t
```
Ship as much as possible, limited by available inventory.

### Step 3: Update Inventory and Backlog
```
I_i,t = I_i,t - S_i,t
B_i,t = B_i,t-1 + IO_i,t - S_i,t
```

### Step 4: Form Expectations (Exponential Smoothing)
```
D^e_t = D^e_{t-1} + θ·(D_observed,t - D^e_{t-1})
```
Where θ = 0.2 (smoothing factor).

### Step 5: Calculate Desired Supply Line
```
SL*_i,t = D^e_i,t · (delay_time)
```
Where delay_time = mailing_delay + shipping_time for intermediate echelons, or production_lead_time for factory.

### Step 6: Place Orders (Anchor-and-Adjust)
```
IA_i,t = (I* - EI_i,t) / sat     # Inventory adjustment
SLA_i,t = (SL* - SL_i,t) / sat   # Supply line adjustment
O_i,t = max(0, floor(D^e_i,t + IA_i,t + SLA_i,t))
```

### Step 7: Calculate Costs
```
TC_i,t = TC_i,t-1 + uihc·I_i,t + ubc·B_i,t
```

## Consumer Demand Pattern
- Weeks 1-4: 4 cases/week (constant)
- Week 5+: 8 cases/week (step increase, then constant)

## Key Model Variants

### Rational (Optimal) Policy
- Order exactly what is demanded (pass-through)
- Or: use optimal control with full information

### Behavioral Policy (Sterman)
- Anchor-and-adjust with bounded rationality
- Underweighting of supply line (β << 1)

### Information Sharing
- Allow upstream agents to see retail demand directly
- Use actual consumer demand for D^e instead of local incoming orders

## Sources
- [JASSS - A Mathematical Model of the Beer Game](https://www.jasss.org/17/4/2.html)
- [Transentis - Simulating the Beer Game](https://www.transentis.com/blog/simulating-the-beer-game)
