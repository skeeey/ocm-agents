# Multi-Agents for Open Cluster Management

## Install a Local OCM

```bash
# install clusteradm
curl -L https://raw.githubusercontent.com/open-cluster-management-io/clusteradm/main/install.sh | bash
# create OCM
curl -L https://raw.githubusercontent.com/open-cluster-management-io/OCM/main/solutions/setup-dev-environment/local-up.sh | bash
```

## Multi-Agents for the Open Cluster Management

### Interact with the kubernetes environment

  ```mermaid
  ---
  title: Kubernetes Engineer + Executor
  ---
  stateDiagram-v2
      Manager --> User
      Manager --> Engineer
      Manager --> Executor
  ```

- User: The user who ask questions and give tasks

- Executor: Execute the code written by the Engineer and report the result to it
  
- Engineer: Analyze the User's plan or intent to write a sequence of shell command/scripts

#### Operations on Global Hub and OCM

<div style="display: flex; gap: 5px;">
  <a href="https://asciinema.org/a/673721" target="_blank">
    <img src="https://asciinema.org/a/673721.svg" style="width: 48%; height: auto;" />
  </a>
  
  <a href="https://asciinema.org/a/673715" target="_blank">
    <img src="https://asciinema.org/a/673715.svg" style="width: 48%; height: auto;" />
  </a>
</div>

### Add Knowledge of OCM

  ```mermaid
  ---
  title: Multi-Agents for Open Cluster Management
  ---
  stateDiagram-v2
      Manager --> User
      Manager --> Engineer
      Manager --> Executor
      Manager --> Planner
      Manager --> OCMer
  ```

- Planner - Kubernetes multi-cluster troubleshooting engineer, responsible for analyzing issues and creating plans to resolve them

- OCMer - The knowledge repository of OCM(Open Cluster Management) is a valuable resource where you can find solutions and ideas for addressing any multi-cluster issue

#### Check the status of OCM

<!-- [![asciicast](https://asciinema.org/a/673919.svg)](https://asciinema.org/a/673919) -->
<div style="display: flex; gap: 5px;">
  <a href="https://asciinema.org/a/673919" target="_blank">
    <img src="https://asciinema.org/a/673919.svg" style="width: 90%; height: auto;" />
  </a>
</div>

#### Scenario 1: cluster1 status unknown - bootstrap hub kubeconfig is degraded

- Make the bootstrap hub kubeconfig invalid

```bash
# kubectl edit secret bootstrap-hub-kubeconfig -n open-cluster-management-agent --context kind-cluster1
# kubectl edit secret hub-kubeconfig-secret  -n open-cluster-management-agent --context kind-cluster1

kubectl delete secret bootstrap-hub-kubeconfig -n open-cluster-management-agent --context kind-cluster1
kubectl delete secret hub-kubeconfig-secret  -n open-cluster-management-agent --context kind-cluster1
```

- Wait until the status is unknown

```bash
kubectl get mcl cluster1 --context kind-hub
```

- troubleshooting the unknown issue

```python
python main.py "why the status of cluster1 is unknown?"
```

[![asciicast](https://asciinema.org/a/674162.svg)](https://asciinema.org/a/674162)

#### Scenario 2: cluster2 status unknown - disable the klusterlet agent and registration agent

- Scale these 2 agents to 0

```bash
kubectl scale deployment klusterlet -n open-cluster-management --replicas=0 --context kind-cluster2

kubectl scale deployment klusterlet-registration-agent -n open-cluster-management-agent --replicas=0 --context kind-cluster2
```

- Wait until the status is unknown

```bash
kubectl get mcl cluster2 --context kind-hub
```

- Troubleshooting the unknown issue

```shell
python main.py "why the status of cluster2 is unknown"
```

[![asciicast](https://asciinema.org/a/674155.svg)](https://asciinema.org/a/674155)