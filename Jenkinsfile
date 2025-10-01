pipeline {
    agent any

    environment {
        PROJECT_ID   = "bespin-sandbox"
        REGION       = "asia-southeast2"
        CLUSTER_NAME = "cluster-gke-ws"
        REPO         = "flask-mysql"
        IMAGE_NAME   = "flask-mysql-app"
        IMAGE        = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}"
        GCLOUD_KEY   = credentials('sa-jenkins')
        USE_GKE_GCLOUD_AUTH_PLUGIN = "True"
    }

    stages {
        stage('Auth GCP') {
            steps {
                sh '''
                    gcloud auth activate-service-account --key-file=$GCLOUD_KEY
                    gcloud config set project $PROJECT_ID
                    gcloud auth configure-docker ${REGION}-docker.pkg.dev -q
                '''
            }
        }

        stage('Build & Push Docker Image') {
            steps {
                sh '''
                    docker build -t $IMAGE:latest .
                    docker push $IMAGE:latest
                '''
            }
        }

        stage('Get GKE Credentials') {
            steps {
                sh '''
                    gcloud container clusters get-credentials $CLUSTER_NAME --region $REGION --project $PROJECT_ID
                '''
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh '''
                    kubectl set image deployment/flask-mysql-app flask=$IMAGE:latest --record || \
                    kubectl apply -f flask-deployment.yaml

                '''
            }
        }
    }
}
