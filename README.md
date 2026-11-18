## Architecture Overview

The repository contains the source code for the frontend, backend , and database migrations, alongside the CI workflow. For deployment it triggers/calls another repository viz. ci-cd which contains the Kubernetes manifests (managed via Kustomize) and the reusable CD deployment workflow.

### Core Workflows & Data Flow

1. **Semantic Versioning & Build:** A commit triggers the CI pipeline. The pipeline extracts the semantic version (e.g., `v1.3.0`) from the fix version of Jira ticket mentioned in the PR and appends the short SHA to create a strictly immutable Docker tag (eg: `v1.3.0-sha-abcdefg`).
2. **Selective Execution:** Using `paths-filter`, it dynamically determines which components (backend, frontend, db-migrations) were modified and triggers parallel jobs via a build matrix.
3. **Shift-Left Security:** PRs enforce versioning conventions and run Trivy (vulnerability), Hadolint (Dockerfile), and SonarQube scans before allowing merges.
4. **Secure CD Trigger:** The CI workflow uses short-lived GitHub App tokens (`CI_APP_ID`, `CI_APP_PRIVATE_KEY`) to securely trigger and commit into the reusable deployment workflow in the platform repository.

---

##  Key Features & Engineering Practices

### 1. DB-First Deployment Sequencing (State Safety)
Stateful database changes and stateless application code are decoupled to prevent schema mismatches:
* **Strict Sequencing:** The pipeline enforces a `deploy-db` job first. The `deploy-apps` job only triggers if the DB migration succeeds (or is skipped).
* **Fix-Forward Migrations:** To prevent live data loss, database migrations are treated as immutable Kubernetes `Jobs`. The pipeline safely deletes the old Job before applying the new one. If a DB migration fails, the pipeline halts immediately (zero rollback), enforcing a safe fix-forward strategy.

### 2. Automated Diagnostics (`$GITHUB_STEP_SUMMARY`)
If a deployment times out or fails (e.g., CrashLoopBackOff, missing ConfigMap), the pipeline automatically injects a diagnostic report directly into the GitHub Actions UI. The summary includes:
* Live Pod Statuses
* Recent Namespace Events
* Container logs
* Workload configuration details

### 3. Automated Application Rollbacks
If an application deployment (backend/frontend) fails Kubernetes readiness or liveness probes, the pipeline automatically executes rollback and safely reverts the cluster to the previously working image and discards uncommitted Kustomize changes in the runner to maintain an accurate state.

---

### 4. How to use
Pre-Requisites:
  1. Install Docker Engine as kind runs Kubernetes nodes as local containers, so the container daemon must be actively running before you create the cluster.
  2. Install kind (Kubernetes in Docker) so the kind binary is available in your system PATH.
  3. Install kubectl (ideally within one minor version of v1.32) to manage the cluster and run built-in Kustomize commands (kubectl apply -k).
     
Steps to trigger build:
  1. Make a change in any of the components. For using current code, please make change in the backend component for the pipeline to trigger.
  2. Create a PR (Pull Request) to be merged into "main" branch. This triggers a set of pre-checks.
  3. Once the PR is merged, by one of the set reviewers, it triggers a build-and-deploy in dev environment. The code for build & deploy is present in workflows in      ci-cd repository.
  4. Once the build is done, it's pushed to DockerHub registry. The image version is saved in the dev kustomization file which is then used to promote it to            higher environments.
     
Steps to deploy:
  1. Open a CLI in your local machine.
  2. Run below steps one after the other:
      2.1 kind version ( To ensure that kind is installed )
      2.2 kubectl version --client ( To ensure that kubectl is installed )
      2.3 kind create cluster --name dev --image kindest/node:v1.32.2
      2.4 kubectl create namespace dev
      2.5 kubectl apply -k k8s/overlays/dev
      2.6 kubectl get pods -n dev
      2.7 kubectl rollout status deployment/backend -n dev
      2.8 kubectl port-forward deployment/backend 8080:8080 -n dev
  3. Open any browser and hit the url "http://localhost:8080" to see the deployed change.
  
 NOTE:
  Do a "git pull" in your local git repository to fetch the latest kustomization file from ci-cd repository.
  Ensure you are in the project root directory containing the k8s/overlays/dev folder with a valid kustomization.yaml file before you run the deploy steps.

---

##  Repository Structure

### `my-app-code` (App Monorepo)
```text
├── .github/workflows/
│   └── ci-pipeline.yaml      # Detects changes, builds images, triggers CD
├── backend/
│   ├── app.py                # Flask backend serving static assets
│   ├── static/               # Hosted static images
│   └── Dockerfile            # Secures execution via non-root 'appuser'
├── frontend/
└── db-migrations/            # SQL migration scripts
