pipeline {
    agent any

    environment {
        IMAGE_NAME = "shopapi"
        IMAGE_TAG = "${BUILD_NUMBER}"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Install") {
            steps {
                sh """
                    python3 -m venv .venv
                    . .venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -r requirements-dev.txt
                """
            }
        }

        stage("Lint") {
            steps {
                sh """
                    . .venv/bin/activate
                    flake8 app tests
                    black --check app tests
                    isort --check-only app tests
                """
            }
        }

        stage("Test") {
            steps {
                sh """
                    . .venv/bin/activate
                    pytest
                """
            }
        }

        stage("Docker Build") {
            steps {
                sh """
                    docker build \
                        -f docker/Dockerfile \
                        -t ${IMAGE_NAME}:${IMAGE_TAG} \
                        .
                """
            }
        }

        stage("Deploy") {
            when {
                branch "main"
            }

            steps {
                sh """
                    IMAGE_TAG=${IMAGE_TAG} \
                    ./scripts/deploy.sh
                """
            }
        }
    }

    post {
        always {
            junit allowEmptyResults: true,
                  testResults: "**/junit.xml"

            archiveArtifacts(
                artifacts: "coverage.xml",
                allowEmptyArchive: true
            )
        }
    }
}
