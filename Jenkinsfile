pipeline {
    agent any

    parameters {
        choice(
            name: 'ACTION',
            choices: ['build-and-deploy', 'deploy-only', 'release-and-deploy', 'rollout-restart'],
            description: 'Action for Jenkins pipeline'
        )
        string(
            name: 'IMAGE_TAG',
            defaultValue: 'latest',
            description: 'Tag image for deploy (ex: latest, 202510021200)'
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
                script {
                    if (params.ACTION == 'release-and-deploy') {
                        def tag = sh(script: "date +%Y%m%d%H%M", returnStdout: true).trim()
                        env.IMAGE_TAG = tag
                        sh """
                            echo "Building release with tag $IMAGE_TAG"
                            docker build -t $IMAGE:$IMAGE_TAG .
                            docker push $IMAGE:$IMAGE_TAG
                        """
                    } else {
                        env.IMAGE_TAG = "latest"
                        sh """
                            echo "Building image with tag latest"
                            docker build -t $IMAGE:latest .
                            docker push $IMAGE:latest
                        """
                    }
                }
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
                    IMAGE=$(cat image.env | cut -d '=' -f2)

                    if kubectl get deployment $DEPLOYMENT_NAME > /dev/null 2>&1; then
                        echo "Updating image..."
                        kubectl set image deployment/$DEPLOYMENT_NAME $DEPLOYMENT_NAME=$IMAGE --record
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
}
