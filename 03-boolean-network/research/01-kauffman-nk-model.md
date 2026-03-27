# Kauffman NK Boolean Network Model

## Overview
Stuart Kauffman introduced Boolean network models in 1969 for describing gene regulatory networks. The N-K model consists of N nodes, each with exactly K incoming links, forming a directed graph with N nodes and N·K random links.

## Key Properties
- Time is discrete; at each time t, each of N genes is either active (1) or inactive (0)
- State of each gene at t+1 is a Boolean function of K genes at time t
- The K input genes are chosen at random ("quenched" randomness)
- Each node's Boolean function is a random truth table with 2^K entries

## Surprising Order
Kauffman found surprisingly ordered structures in randomly constructed networks:
- Most organized behavior when K=2 (each node receives inputs from 2 others)
- Networks self-organize into short attractor cycles
- Number of attractors scales roughly as √N for K=2

## Biological Interpretation
- Each node represents a gene (on/off)
- The network models gene regulatory interactions
- Attractors represent cell types
- The model explains how ~250 cell types emerge from ~20,000 genes

## Sources
- Kauffman, S.A. (1969). Metabolic stability and epigenesis in randomly constructed genetic nets.
- Kauffman, S.A. (1993). The Origins of Order: Self-Organization and Selection in Evolution.
