# Kubernetes Volumes, Probes & Services Demo

A tiny Python web app packaged with Docker and deployed to Minikube. It demonstrates a PVC, startup/liveness/readiness probes, a NodePort Service, ConfigMap, and resource limits.

## Prerequisites
- Docker Desktop running
- Minikube and kubectl installed
- PowerShell on Windows

## Deploy
Run these commands from this project folder:

```powershell
minikube start --driver=docker
minikube image build -t storage-demo:v1 .
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl -n storage-demo rollout status deployment/storage-demo
kubectl -n storage-demo get pods,pvc,services
minikube service storage-demo -n storage-demo
```

The PVC may take a little time to bind. Check `kubectl -n storage-demo get pvc`.

## Try it
Click **Record a visit**. The timestamp is appended to `/data/visits.txt`.
- `/health/live`: liveness and startup probe endpoint
- `/health/ready`: readiness endpoint; checks the data file can be opened
- `/api/visits`: visit count in JSON

## Check resources and logs
```powershell
kubectl -n storage-demo describe pod
kubectl -n storage-demo logs deployment/storage-demo
kubectl -n storage-demo get events --sort-by=.metadata.creationTimestamp
kubectl -n storage-demo describe pvc visits-pvc
```

## Test persistence
1. Record a few visits.
2. Delete the Pod: `kubectl -n storage-demo delete pod -l app=storage-demo`
3. Wait for the replacement Pod, then refresh. The visit count should remain because the file is stored on the PVC.

## Cleanup
```powershell
kubectl delete namespace storage-demo
minikube stop
```
Deleting the namespace deletes the PVC claim. Whether underlying storage is retained depends on the cluster's storage provisioner and reclaim policy. Back up any important data first.
