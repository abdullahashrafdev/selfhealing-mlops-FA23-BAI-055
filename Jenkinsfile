pipeline {
    agent any

    environment {
        DOCKERHUB_USER = "abdullahsdocker"
        UNSTABLE_IMAGE = "${DOCKERHUB_USER}/sentiment-api:unstable"
        STABLE_IMAGE   = "${DOCKERHUB_USER}/sentiment-api:stable"
        APP_PORT       = "5000"
        CONTAINER_NAME = "sentiment-app-test"
    }

    stages {

        stage('Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build and Run') {
            steps {
                sh '''
                    docker build -t ${UNSTABLE_IMAGE} .
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 ${UNSTABLE_IMAGE}
                    sleep 10
                '''
            }
        }

        stage('Unit Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -e BASE_URL=http://localhost:${APP_PORT} \
                        -v ${WORKSPACE}/tests:/tests \
                        ${UNSTABLE_IMAGE} \
                        bash -c "pip install pytest requests --quiet && pytest /tests/test_api.py -v"
                '''
            }
        }

        stage('UI Test') {
            steps {
                sh '''
                    docker run --rm \
                        --network host \
                        -v ${WORKSPACE}/tests:/tests \
                        selenium/standalone-chrome:latest \
                        bash -c "pip install pytest selenium --quiet && pytest /tests/test_ui.py -v"
                '''
            }
        }

        stage('Build and Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin

                        # Build and push unstable image from main branch
                        docker build -t ${UNSTABLE_IMAGE} .
                        docker push ${UNSTABLE_IMAGE}

                        # Build and push stable image from stable-fallback branch
                        git fetch origin stable-fallback
                        git checkout origin/stable-fallback -- app.py
                        docker build -t ${STABLE_IMAGE} .
                        docker push ${STABLE_IMAGE}

                        # Restore main branch app.py
                        git checkout HEAD -- app.py
                    '''
                }
            }
        }

        stage('Deploy to Minikube') {
            steps {
                sh '''
                    export KUBECONFIG=$HOME/.kube/config

                    kubectl apply -f k8s/pvc.yaml
                    kubectl apply -f k8s/blue-deployment.yaml
                    kubectl apply -f k8s/green-deployment.yaml
                    kubectl apply -f k8s/service.yaml

                    kubectl rollout status deployment/sentiment-blue-deployment --timeout=120s
                    kubectl rollout status deployment/sentiment-green-deployment --timeout=120s
                '''
            }
        }

    }

    post {
        always {
            sh 'docker rm -f ${CONTAINER_NAME} || true'
        }
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check logs above.'
        }
    }
}
