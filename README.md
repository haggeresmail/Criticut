# **CritiCut — Critical Node Moderation with Edge Removal**

CritiCut is an interactive **network resilience and vulnerability analysis platform** that identifies the most critical nodes and fragile connections in a graph, then intelligently removes risky edges to strengthen the network without breaking it.

It blends **graph theory, linear algebra, and simulation** to model how real-world systems behave under failure — from communication networks and cloud infrastructure to social and transportation networks.

---

## 🚀 What CritiCut Does

CritiCut takes a network and answers one powerful question:

> *“If this network starts to fail, where will it break first — and how can we prevent it?”*

The system:

- Computes **information centrality** using the **graph Laplacian and its pseudo-inverse** to measure how important each node is to overall connectivity  
- Identifies **critical nodes** whose instability would have the largest impact on the network  
- Analyzes each connected edge using **effective resistance**, a metric from electrical network theory that reveals how fragile or redundant a connection is  
- Removes the most vulnerable edges **only if the network remains connected**, reducing cascading-failure risk  
- Visualizes the network before and after optimization  
- Generates a detailed log of every edge removal  

---

## 🧠 Why This Is Powerful

CritiCut does not guess.  
It uses **mathematical models of connectivity** to understand how information, traffic, or power flows through a network — and where it is most likely to collapse.

This makes it applicable to:

- Cloud and data-center reliability  
- Cybersecurity and attack-surface analysis  
- Power-grid and infrastructure modeling  
- Social-network influence and stability  

---

## 🔥 Key Features

- Laplacian-based **information centrality** to detect high-impact nodes  
- **Effective resistance** to rank fragile edges  
- Safe edge removal that preserves global connectivity  
- Real-time graph visualization (interactive and static)  
- Support for uploaded datasets and synthetic networks  
- Downloadable optimization logs for full transparency  

---

## 🛠 Technology Stack

- **Python** – core algorithms and simulation  
- **NetworkX** – graph modeling and traversal  
- **NumPy & SciPy** – Laplacian matrices and linear-algebra computations  
- **Plotly & Matplotlib** – graph visualization  
- **Streamlit** – interactive web interface  

---

## 🎯 Why CritiCut Stands Out

Most graph projects simply **draw networks**.

CritiCut **understands** them.

It shows how failures propagate, which components matter most, and how to make a network more resilient — the same kind of analysis used in real-world infrastructure and reliability engineering.

