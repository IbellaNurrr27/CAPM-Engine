# 📈 CAPM Yield Engine v1.0

A high-fidelity Python CLI utility for calculating the **Expected Return on Assets** using the Capital Asset Pricing Model. Designed for finance students and portfolio managers who value precision and terminal-based efficiency.

> **Formula:** $E(R_i) = R_f + \beta(E(R_m) - R_f)$

---

## 🚀 Overview

The **CAPM Yield Engine** automates the calculation of asset returns by factoring in systematic risk (Beta) and market premiums. Built with a focus on **Data Science** standards and **UI Aesthetics**, it provides a seamless workflow from raw input to exported financial reports.

## ✨ Features

* **Intelligent Parsing:** Accepts inputs as decimals (`0.05`) or percentages (`5%`).
* **Market Risk Premium (MRP) Analytics:** Automatically isolates the premium for deeper risk analysis.
* **Risk Profiling:** Classifies assets based on volatility (Defensive, Aggressive, High Risk).
* **Data Persistence:** Uses `pandas` to aggregate multiple assets and export sessions to **CSV**.
* **Rich Terminal UI:** Featuring ASCII banners, progress spinners, and formatted tables for a professional "Bloomberg Terminal" feel.

## 🛠️ Tech Stack

* **Language:** Python 3.14+
* **Libraries:** * `pandas` (Data Manipulation)
    * `rich` (Terminal Formatting & UI)
    * `datetime` (Session Logging)

## 🏎️ Getting Started

1. **Clone the repository**
   ```bash
   git clone [https://github.com/IbellaNurrr27/CAPM-Engine.git](https://github.com/IbellaNurrr27/CAPM-Engine.git)
