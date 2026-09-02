# PulseWatch sur Kubernetes local

Ce dossier contient une configuration Kubernetes volontairement simple pour exécuter PulseWatch avec kind. Elle lance deux pods API, un pod PostgreSQL et un CronJob qui contrôle les services toutes les cinq minutes.

## Prérequis

Docker, `kubectl` et [kind](https://kind.sigs.k8s.io/) doivent être installés.

## Créer le cluster et charger l'image

Depuis la racine du dépôt :

```bash
kind create cluster --name pulsewatch
docker build -t pulsewatch-api:local .
kind load docker-image pulsewatch-api:local --name pulsewatch
```

Le déploiement utilise `imagePullPolicy: IfNotPresent`, afin que kind utilise l'image chargée localement. Un conteneur d'initialisation attend que PostgreSQL accepte les connexions avant de démarrer l'API.

## Créer le secret local

```bash
kubectl apply -f k8s/namespace.yaml
kubectl create secret generic pulsewatch-db-secret --namespace pulsewatch --from-literal=POSTGRES_PASSWORD='choisir-un-mot-de-passe-local'
```

Il est aussi possible de copier `secret.example.yaml` vers `secret.yaml`, de remplacer le texte d'exemple et d'appliquer le fichier. `secret.yaml` est ignoré par Git. Ne jamais utiliser un secret réel ou réutilisé dans le modèle d'exemple.

## Appliquer les ressources

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/api-deployment.yaml
kubectl apply -f k8s/api-service.yaml
kubectl apply -f k8s/cronjob.yaml
kubectl rollout status deployment/postgres -n pulsewatch
kubectl rollout status deployment/pulsewatch-api -n pulsewatch
```

## Observer l'application

```bash
kubectl get pods -n pulsewatch
kubectl get deployments -n pulsewatch
kubectl get services -n pulsewatch
kubectl logs -n pulsewatch deployment/pulsewatch-api --all-pods=true
kubectl port-forward -n pulsewatch service/pulsewatch-api 8000:8000
```

Ouvrir ensuite <http://localhost:8000/>. Les exécutions du CronJob se consultent avec `kubectl get cronjobs,jobs -n pulsewatch`.

## Tester l'auto-réparation et le dimensionnement

```bash
kubectl scale deployment/pulsewatch-api --replicas=3 -n pulsewatch
kubectl get pods -n pulsewatch -w
kubectl delete pod -n pulsewatch "$(kubectl get pods -n pulsewatch -l app=pulsewatch-api -o jsonpath='{.items[0].metadata.name}')"
kubectl get pods -n pulsewatch -w
```

## Nettoyer

```bash
kubectl delete namespace pulsewatch
kind delete cluster --name pulsewatch
```
