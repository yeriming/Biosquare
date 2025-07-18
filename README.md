# Biosquare: A Visual Simulation of Natural Selection

This project is a Python-based evolutionary simulation that models predator-prey dynamics between wolves and deer, inspired by Charles Darwin’s example in *On the Origin of Species* (Chapter 4). The simulation uses mutation, inheritance, and reproduction logic to demonstrate how traits evolve over time through natural selection.

---

**This project was developed as a final assignment for the course**  
**“Infinity and the Evolution of Intelligence”**  
taught by **Professor Daniel Louis Nethery** at **Freie Universität Berlin (SoSe 2025)**.

---

## Purpose

This simulation was designed primarily for educational use, helping students understand core concepts in evolution:
- How random mutation introduces variation
- How selection pressure influences survival
- How traits can become more common over generations

It is especially aimed at students with little to no background in evolutionary biology or Python programming.

## How It Works

- Wolves hunt deer on a 2D grid using `pygame`
- Each animal has traits: `speed` and `sight`
- Offspring inherit traits from parents, with possible mutation
- Survival affects reproduction — not all animals get to reproduce
- Evolutionary trends can be visualized using logged statistics

## Key Features

- `mutate_trait(rate, strength, trait)`: introduces small, random trait changes  
- `reproduce()`: survival-based reproduction system for both species  
- `log_population_stats`: records trait averages and population size per step  
- `mutation_stats`: tracks mutation count and magnitude for each step  
- A final dashboard image shows evolutionary outcomes over time

## Educational Goals

This simulation can be used to:
- Run and observe natural selection in action  
- Test hypotheses (e.g. “do faster deer survive longer?”)  
- Analyze trait evolution using visual graphs  
- Learn Python coding practices in an applied context

The code is written with clear structure and inline comments to support learning and self-guided exploration.

## Requirements

- Python 3.8+  
- `pygame`, `matplotlib`, `numpy`
