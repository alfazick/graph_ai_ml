# arXiv Document Graph Analysis Report
Generated on: 2024-12-31 03:32:32

This report analyzes the similarity relationships between arXiv research papers.


## Step 1: Basic Graph Statistics

Overview of the document graph structure and size.


## Total Documents

Number of research papers in the graph.

```
+------------------+
|   document_count |
|------------------|
|            50426 |
+------------------+
```


## Total Relationships

Number of similarity connections between papers.

```
+----------------------+
|   relationship_count |
|----------------------|
|          2.54385e+07 |
+----------------------+
```


## Category Distribution

Top 10 research categories by number of papers.

```
+------------+---------+
| category   |   count |
|------------+---------|
| math.ST    |     375 |
| stat.TH    |     375 |
| stat.ML    |     341 |
| cs.LG      |     284 |
| stat.ME    |     234 |
| stat.AP    |     155 |
| math.PR    |      88 |
| stat.CO    |      67 |
| cs.AI      |      58 |
| cs.CV      |      31 |
+------------+---------+
```


## Step 2: Machine Learning Papers Analysis

Analysis of papers in Machine Learning and Statistical Learning categories.


## Most Similar ML Papers

Top 10 most similar pairs of Machine Learning papers.

```
+-------------+------------------------------------------------------------------------------------------------------+-------------+-------------------------------------------------------------------+--------------+
|   source_id | source_title                                                                                         |   target_id | target_title                                                      |   similarity |
|-------------+------------------------------------------------------------------------------------------------------+-------------+-------------------------------------------------------------------+--------------|
|     1805.08 | Quantizing Convolutional Neural Networks for Low-Power High-Throughput Inference Engines             |     1810.05 | Efficient Augmentation via Data Subsampling                       |            1 |
|     1805.02 | Branching embedding: A heuristic dimensionality reduction algorithm based on hierarchical clustering |     1902.01 | Spaces of Clusterings                                             |            1 |
|     1805.08 | Featurized Bidirectional GAN: Adversarial Defense via Adversarially Learned Semantic Inference       |     1901.1  | Measuring the Robustness of Graph Properties                      |            1 |
|     1805.08 | Featurized Bidirectional GAN: Adversarial Defense via Adversarially Learned Semantic Inference       |     1901.08 | On the Transformation of Latent Space in Autoencoders             |            1 |
|     1805.08 | Learning Device Models with Recurrent Neural Networks                                                |     1812.08 | Bayesian parameter estimation of miss-specified models            |            1 |
|     1805.08 | Learning Device Models with Recurrent Neural Networks                                                |     1811.04 | Convolutional neural networks in phase space and inverse problems |            1 |
|     1805.08 | Learning Device Models with Recurrent Neural Networks                                                |     1810.09 | Assessing the Stability of Interpretable Models                   |            1 |
|     1805.08 | Learning with Non-Convex Truncated Losses by SGD                                                     |     1902.03 | Generating the support with extreme value losses                  |            1 |
|     1805.08 | Learning with Non-Convex Truncated Losses by SGD                                                     |     1901.1  | Measuring the Robustness of Graph Properties                      |            1 |
|     1805.08 | Learning with Non-Convex Truncated Losses by SGD                                                     |     1812.08 | Bayesian parameter estimation of miss-specified models            |            1 |
+-------------+------------------------------------------------------------------------------------------------------+-------------+-------------------------------------------------------------------+--------------+
```


## Step 3: Cross-Category Analysis

Analysis of similarities between papers from same vs different categories.


## Category Connection Analysis

Comparison of similarity scores between papers from same vs different categories.

```
+--------------------+------------------+-------------------+
| connection_type    |   avg_similarity |   num_connections |
|--------------------+------------------+-------------------|
| same_category      |           0.0792 |               101 |
| different_category |           1      |               899 |
+--------------------+------------------+-------------------+
```


## Step 4: Paper Clusters

Finding groups of three papers that are all highly similar to each other (similarity > 0.9).
