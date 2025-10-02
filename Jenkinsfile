pipeline {
    agent any

    parameters {
        choice(
            name: 'ACTION',
            choices: ['build-and-deploy', 'deploy-only', 'release-and-deploy', 'rollout-restart'],
            description: 'action for jenkins'
        )
    }

    environment {
        PROJECT_ID   = "bespin-sandbox"
        REGION       = "asia-southeast2"
        CLUSTER_NAME = "cluster-gke-ws"
        REPO         = "flask-mysql"
        IMAGE_NAME   = "flask-mysql-app"
        IMAGE        = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${IMAGE_NAME}"
        GCLOUD_KEY   = credentials('sa-jenkins')
        USE_GKE_GCLOUD_AUTH_PLUGIN = "True"
        DEPLOYMENT_NAME = "flask-mysql-app"
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
            when { expression { params.ACTION == 'build-and-deploy' || params.ACTION == 'release-and-deploy' } }
            steps {
                sh '''
                    docker build -t $IMAGE:latest .
                    docker push $IMAGE:latest
                '''
            }
        }

            steps {
                sh '''
                    if [ "$ACTION" = "release-and-deploy" ]; then
                        TAG=$(date +%Y%m%d%H%M)
                        echo "Building release with tag $TAG"
                        docker build -t $IMAGE:$TAG .
                        docker push $IMAGE:$TAG
                        echo "IMAGE=$IMAGE:$TAG" > image.env
                    else
                        docker build -t $IMAGE:latest .
                        docker push $IMAGE:latest
                        echo "IMAGE=$IMAGE:latest" > image.env
                    fi
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
            when { expression { params.ACTION == 'build-and-deploy' || params.ACTION == 'deploy-only' || params.ACTION == 'release-and-deploy' } }
            steps {
                sh '''
                    if kubectl get deployment $DEPLOYMENT_NAME > /dev/null 2>&1; then
                        echo "Updating image..."
                        kubectl set image deployment/$DEPLOYMENT_NAME $DEPLOYMENT_NAME=$IMAGE:latest --record
                    else
                        echo "Deployment not found, creating from YAML..."
                        kubectl apply -f flask-deployment.yaml
                    fi

                    if ! kubectl rollout status deployment/$DEPLOYMENT_NAME; then
                        echo "Rollout failed, rolling back..."
                        kubectl rollout undo deployment/$DEPLOYMENT_NAME
                        exit 1
                    fi

                    echo "Deployment successful!"
                '''
            }
        }

        stage('Rollout Restart') {
            when { expression { params.ACTION == 'rollout-restart' } }
            steps {
                sh '''
                    kubectl rollout restart deployment/$DEPLOYMENT_NAME
                    kubectl rollout status deployment/$DEPLOYMENT_NAME
                '''
            }
        }
    }