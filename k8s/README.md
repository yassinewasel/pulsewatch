# PulseWatch on kind

This directory contains a deliberately small local Kubernetes setup for learning and
testing PulseWatch. It runs two API Pods, one PostgreSQL Pod, and a CronJob that checks
all configured services every five minutes.

## Prerequisites

Install Docker, `kubectl`, and [kind](https://kind.sigs.k8s.io/).

## Create the cluster and load the image

Run these commands from the repository root:

```bash
kind create cluster --name pulsewatch
docker build -t pulsewatch-api:local .
kind load docker-image pulsewatch-api:local --name pulsewatch
```

The API Deployment uses `imagePullPolicy: IfNotPresent`, so kind uses the image loaded
into its nodes instead of trying to pull it from a registry.

Each API Pod has a small init container that waits for PostgreSQL to accept connections
before starting PulseWatch. The regular liveness and readiness probes then monitor the
running API container.

## Create the local secret

Create the namespace first, then create the Secret directly without writing its value
to a tracked file:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl create secret generic pulsewatch-db-secret \
  --namespace pulsewatch \
  --from-literal=POSTGRES_PASSWORD='choose-a-local-password'
```

Alternatively, copy `k8s/secret.example.yaml` to `k8s/secret.yaml`, replace the
placeholder, and apply it. `k8s/secret.yaml` is ignored by Git:

```bash
cp k8s/secret.example.yaml k8s/secret.yaml
kubectl apply -f k8s/secret.yaml
```

Never put a real or reused password in `secret.example.yaml`.

## Apply the resources

Apply the remaining manifests explicitly so the example Secret is never applied by
accident:

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/cronjob.yaml
```

Wait for the workloads:

```bash
kubectl rollout status deployment/postgres -n pulsewatch
kubectl rollout status deployment/pulsewatch-api -n pulsewatch
```

## Inspect and use PulseWatch

```bash
kubectl get pods -n pulsewatch
kubectl get deployments -n pulsewatch
kubectl get services -n pulsewatch
kubectl logs -n pulsewatch deployment/pulsewatch-api --all-pods=true
kubectl logs -n pulsewatch deployment/postgres
kubectl port-forward -n pulsewatch service/pulsewatch-api 8000:8000
```

With port forwarding running, open <http://localhost:8000/>.

To inspect CronJob executions:

```bash
kubectl get cronjobs,jobs -n pulsewatch
kubectl logs -n pulsewatch job/<job-name>
```

## Practice self-healing and scaling

Scale the API Deployment:

```bash
kubectl scale deployment/pulsewatch-api --replicas=3 -n pulsewatch
kubectl get pods -n pulsewatch -w
```

Delete one API Pod and watch the Deployment replace it:

```bash
kubectl delete pod -n pulsewatch "$(kubectl get pods -n pulsewatch -l app=pulsewatch-api -o jsonpath='{.items[0].metadata.name}')"
kubectl get pods -n pulsewatch -w
```

## Clean up

Delete all PulseWatch resources, including the PVC and its local data:

```bash
kubectl delete namespace pulsewatch
```

Delete the entire kind cluster:

```bash
kind delete cluster --name pulsewatch
```
