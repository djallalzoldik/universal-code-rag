# Deployment Guide

## Quick Start

### Docker (Recommended)

```bash
# Build the image
docker build -t chrome-rag .

# Run with help
docker run --rm chrome-rag --help

# Index files
docker run --rm \
  -v /path/to/source:/source \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  chrome-rag index --path /source

# Search
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  chrome-rag search --query "your query"
```

### Docker Compose (Production)

```bash
# Start service
docker-compose -f docker-compose.prod.yml up -d

# Index files
docker-compose -f docker-compose.prod.yml exec chrome-rag \
  python cli.py index --path /source

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop service
docker-compose -f docker-compose.prod.yml down
```

---

## Production Deployment

### 1. Environment Variables

```bash
export DB_PATH=/app/chrome_rag_db
export LOG_LEVEL=INFO
```

### 2. Volume Mounts

**Required**:
- `chrome_rag_db`: Database persistence
- `source`: Source code to index (read-only)
- `logs`: Application logs

### 3. Health Checks

Health check runs every 30 seconds:
```bash
docker inspect --format='{{json .State.Health}}' chrome-rag-prod
```

### 4. Resource Limits

The production compose file sets:
- CPU: 1-2 cores
- Memory: 2-4GB

Adjust in `docker-compose.prod.yml` as needed.

---

## Kubernetes Deployment

### Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chrome-rag
spec:
  replicas: 1
  selector:
    matchLabels:
      app: chrome-rag
  template:
    metadata:
      labels:
        app: chrome-rag
    spec:
      containers:
      - name: chrome-rag
        image: chrome-rag:latest
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "1"
            memory: "2Gi"
        livenessProbe:
          exec:
            command:
            - python
            - health_check.py
          initialDelaySeconds: 10
          periodSeconds: 30
        volumeMounts:
        - name: db
          mountPath: /app/chrome_rag_db
      volumes:
      - name: db
        persistentVolumeClaim:
          claimName: chrome-rag-db

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: chrome-rag-db
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

Apply with:
```bash
kubectl apply -f k8s-deployment.yaml
```

---

## Cloud Deployments

### AWS ECS

1. Push image to ECR
2. Create task definition with volume mounts
3. Set up EFS for database persistence
4. Configure health checks

### Google Cloud Run

```bash
gcloud run deploy chrome-rag \
  --image gcr.io/PROJECT/chrome-rag \
  --memory 4Gi \
  --cpu 2
```

### Azure Container Instances

```bash
az container create \
  --name chrome-rag \
  --image chrome-rag:latest \
  --cpu 2 \
  --memory 4
```

---

## Monitoring

### Health Check Endpoint

```bash
# Check container health
docker exec chrome-rag python health_check.py
```

### Logs

```bash
# Docker logs
docker logs -f chrome-rag-prod

# Docker Compose logs
docker-compose -f docker-compose.prod.yml logs -f

# Kubernetes logs
kubectl logs -f deployment/chrome-rag
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs chrome-rag-prod

# Verify image
docker images | grep chrome-rag

# Test health check manually
docker run --rm chrome-rag python health_check.py
```

### Database Issues

```bash
# Clear database
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  chrome-rag clear --yes

# Check stats
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  chrome-rag stats
```

### Performance Issues

- Increase memory: Edit `docker-compose.prod.yml`
- Add more CPUs: Increase resource limits
- Enable parallel processing: Default behavior

---

## CI/CD

The project includes GitHub Actions for:
- ✅ Automated testing on push
- ✅ Docker image building
- ✅ Image size verification

View status: https://github.com/YOUR_ORG/chrome-rag-system/actions

---

## Security

### Best Practices

1. **Don't run as root**: Add USER directive (optional)
2. **Read-only mounts**: Use `:ro` for source code
3. **Network isolation**: Use Docker networks
4. **Resource limits**: Set CPU/memory limits
5. **Regular updates**: Rebuild images regularly

### Scanning

```bash
# Scan for vulnerabilities
docker scan chrome-rag:latest

# Check with trivy
trivy image chrome-rag:latest
```

---

## Backup & Recovery

### Backup Database

```bash
# Backup
tar -czf chrome_rag_db_backup.tar.gz chrome_rag_db/

# Restore
tar -xzf chrome_rag_db_backup.tar.gz
```

### Export Data

```bash
# Get statistics
docker run --rm \
  -v $(pwd)/chrome_rag_db:/app/chrome_rag_db \
  chrome-rag stats > stats.txt
```

---

## Scaling

### Horizontal Scaling

For read-heavy workloads:
1. Deploy multiple read replicas
2. Use load balancer
3. Share database volume (read-only)

### Vertical Scaling

Increase resources in `docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4.0'
      memory: 8G
```

---

## Support

- **Issues**: https://github.com/YOUR_ORG/chrome-rag-system/issues
- **Documentation**: README.md
- **CI/CD Status**: GitHub Actions tab
