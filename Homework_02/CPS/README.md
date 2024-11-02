# CSP Framework

This repository provides a **Constraint Satisfaction Problem (CSP) framework** that can serve as a flexible blueprint for solving various constraint-based problems, such as the **N-Queens problem** and **map coloring**.

The framework follows a generic structure that allows for easy modification and extension with custom constraints, making it adaptable to different CSP scenarios. The current implementation primarily uses **backtracking** to find solutions. While this is effective for many problems, it may not be the most efficient approach for all cases. In practice, a specialized algorithm like **min-conflicts** or **forward-checking** may yield better performance for specific problems.

## Key Components

1. **Constraint Class**: A base class for defining custom constraints between variables. This can be tailored to fit the specific rules of the CSP being modeled.
2. **CSP Class**: The core class for setting up variables, domains, and constraints, and solving the CSP through a backtracking search. The `consistent` method checks if assignments meet the constraints, while the `backtracking_search` method attempts to find a solution by iteratively assigning values and checking for consistency.

## Usage Examples

The repository includes examples demonstrating how this CSP framework can be applied to:
- **N-Queens Problem**: Finding placements for queens on an \( N \times N \) chessboard so that no two queens threaten each other.
- **Map Coloring**: Assigning colors to regions on a map such that no adjacent regions share the same color.

These examples illustrate the framework's capabilities but are generic implementations and not necessarily optimized for performance. You may consider integrating more advanced algorithms, such as min-conflicts, to improve efficiency for specific problems.