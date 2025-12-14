pipeline {
    agent any

    environment {
        IMAGE_NAME = "yourdockerhubusername/flask-ci-cd-app"
    }

    stages {

        stage('Code Fetch') {
            steps {
                git branch: 'main',
                url: 'https://github.com/yourusername/sample-ci-cd-project.git'
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
                sh 'kubectl apply -f k8s/'
            }
        }
    }
}
