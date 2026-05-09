# To-Do List App

A simple Flask web application for managing tasks with deadline tracking. Built primarily to practice a full DevOps pipeline from code to deployment.

---

## Features

- Add and delete tasks with optional deadlines
- Background scheduler checks every minute for overdue tasks
- SQLite database (auto-created on first run, zero setup)
- REST API with a vanilla JS frontend

---

## Tech Stack

### Application
| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-APScheduler |
| Frontend | HTML, CSS, JavaScript (Vanilla) |
| Database | SQLite |

### DevOps Pipeline
| Stage | Tool |
|---|---|
| Containerization | Docker |
| CI/CD | Jenkins (Declarative Pipeline) |
| Container Registry | Docker Hub |
| Orchestration | Kubernetes (3 replicas, NodePort service) |
| GitOps | ArgoCD |
| Cloud Provider | AWS |

---

## Project Structure

```
To-Do-List/
├── app.py                  # Flask app
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image definition
├── Jenkinsfile             # CI/CD pipeline (build → push → update manifest)
├── K8s/
│   ├── deployment.yaml    
│   └── service.yaml   
└── templates/
    └── index.html          # Frontend UI
```

---

## CI/CD Pipeline

The Jenkins pipeline runs automatically on every push and does the following:

1. **Clone** — pulls the latest code from GitHub
2. **Build** — builds a Docker image tagged with the Jenkins build number
3. **Push** — logs into Docker Hub and pushes the image
4. **GitOps update** — updates `K8s/deployment.yaml` with the new image tag and pushes the change back to GitHub
5. **ArgoCD** — detects the manifest change and syncs the new image to the Kubernetes cluster
6. **Cleanup** — runs `docker system prune` on the agent after every build

---

## Running Locally

### Without Docker

```bash
pip install -r requirements.txt
python app.py
```

App runs at `http://localhost:5000`

### With Docker

```bash
docker build -t todo-list .
docker run -p 5000:5000 todo-list
```

## Kubernetes Deployment

```bash
kubectl apply -f K8s/deployment.yaml
kubectl apply -f K8s/service.yaml
```

Access the app at `http://<node-ip>:30080`



