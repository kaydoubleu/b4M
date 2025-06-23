# 🌅📊🙌 b4M - Holistic Benchmarking for MPC

This is the initial repository of b4M with the relevant code for the respective paper;
please stay tuned and monitor this repository for updates in the upcoming weeks (benchmarking summer of 2025 🌅😊)

## 📜 the Paper

Secure Multi-Party Computation (MPC) is becoming more and more usable in practice. The practicality origins primarily from well-established general-purpose MPC frameworks, such as MP-SPDZ. However, to evaluate the practicality of an MPC program in the envisioned environments, still many benchmarks need to be done. We identified three challenges in the context of performance evaluations within the MPC domain: first, the cumbersome process to holistically benchmark MPC programs; second, the difficulty to find the best-possible MPC setting for a given task and envisioned environment; and third, to have consistent evaluations of the same task or problem area across projects and papers. In this work, we address the gap of tedious and complex benchmarking of MPC. Related works so far mostly provide a comparison for certain programs with different engines.

To the best of our knowledge, for the first time the whole benchmarking pipeline is automated; provided by our open-sourced framework Holistic Benchmarking for MPC (b4M). b4M is easy to configure using TOML files, outputs ready-to-use graphs, and provides even the MPC engine itself as own benchmark dimension. Furthermore it takes three relatively easy steps to add further engines: first, integrate engine-specific commands into b4M’s runner class; second, output performance metrics in b4M’s format; third, provide a Docker container for the engine’s parties.

To showcase b4M, we provide an exemplary evaluation for the computation of the dot product and logistic regression using a real-world dataset. With this work, we move towards fully-automated evaluations of MPC programs, protocols, and engines, which smoothens the setup process and viewing various trade-offs. Hence, b4M advances MPC development by improving the benchmarking usability aspect of it.

**@ePrint:**
```
@misc{cryptoeprint:2025/1106,
      author = {Karl W. Koch and Dragos Rotaru and Christian Rechberger},
      title = {{b4M}: Holistic Benchmarking for {MPC}},
      howpublished = {Cryptology {ePrint} Archive, Paper 2025/1106},
      year = {2025},
      url = {https://eprint.iacr.org/2025/1106}
}
```
