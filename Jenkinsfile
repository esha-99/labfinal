pipeline {
    agent any
    environment {
        IMAGE_NAME = "eshashamraiz2004/flask-ci-cd-app"
    }
    stages {
        stage('Code Fetch') {
            steps {
                git branch: 'main',
                url: 'https://github.com/esha-99/labfinal'
            }
        }
        stage('Docker Build') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:latest")
                }
            }
        }
        stage('Docker Push') {
            steps {
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                        docker.image("${IMAGE_NAME}:latest").push()
                    }
                }
            }
        }
        stage('Kubernetes Deploy') {
            steps {
                withEnv(["KUBECONFIG=/var/lib/jenkins/.kube/config"]) {
                    sh '''
                        echo "Deploying application..."
                        kubectl apply -f k8s/pvc.yaml
                        kubectl apply -f k8s/mysql-deployment.yaml
                        kubectl apply -f k8s/mysql-service.yaml
                        kubectl apply -f k8s/deployment.yaml
                        kubectl apply -f k8s/service.yaml
                        echo "Application deployed successfully!"
                    '''
                }
            }
        }
        stage('Deploy Monitoring Stack') {
            steps {
                withEnv(["KUBECONFIG=/var/lib/jenkins/.kube/config"]) {
                    sh '''
                        echo "Deploying Prometheus and Grafana..."
                        kubectl apply -f k8s/monitoring/prometheus-rbac.yaml
                        kubectl apply -f k8s/monitoring/prometheus-config.yaml
                        kubectl apply -f k8s/monitoring/prometheus-deployment.yaml
                        kubectl apply -f k8s/monitoring/prometheus-service.yaml
                        kubectl apply -f k8s/monitoring/grafana-deployment.yaml
                        kubectl apply -f k8s/monitoring/grafana-service.yaml
                        
                        echo "Waiting for Prometheus to be ready..."
                        kubectl wait --for=condition=ready pod -l app=prometheus --timeout=300s || true
                        
                        echo "Waiting for Grafana to be ready..."
                        kubectl wait --for=condition=ready pod -l app=grafana --timeout=300s || true
                        
                        echo "Monitoring stack deployed successfully!"
                    '''
                }
            }
        }
        stage('Verify Deployment') {
            steps {
                withEnv(["KUBECONFIG=/var/lib/jenkins/.kube/config"]) {
                    sh '''
                        echo "=========================================="
                        echo "         DEPLOYMENT VERIFICATION          "
                        echo "=========================================="
                        echo ""
                        echo "=== Deployments ==="
                        kubectl get deployments
                        echo ""
                        echo "=== Pods ==="
                        kubectl get pods
                        echo ""
                        echo "=== Services ==="
                        kubectl get svc
                        echo ""
                        echo "=========================================="
                        echo "           ACCESS INFORMATION             "
                        echo "=========================================="
                        echo "Flask App URL:"
                        minikube service flask-app --url || echo "Run: minikube service flask-app"
                        echo ""
                        echo "Prometheus URL:"
                        minikube service prometheus --url || echo "Run: minikube service prometheus"
                        echo ""
                        echo "Grafana URL:"
                        minikube service grafana --url || echo "Run: minikube service grafana"
                        echo "Grafana Credentials: admin / admin123"
                        echo "=========================================="
                    '''
                }
            }
        }
    }
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo '📊 Access your monitoring dashboards:'
            echo '   - Prometheus: minikube service prometheus'
            echo '   - Grafana: minikube service grafana (admin/admin123)'
        }
        failure {
            echo '❌ Pipeline failed. Check logs for details.'
        }
        always {
            echo 'Pipeline execution finished.'
        }
    }
}
