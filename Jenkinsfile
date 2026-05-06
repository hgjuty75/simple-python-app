pipeline {
    agent any

    parameters {
        string(name: 'STUDENT_NAME', defaultValue: 'Иванов Иван', description: 'ФИО студента')
        choice(name: 'ENVIRONMENT', choices: ['dev', 'staging', 'production'], description: 'Среда развертывания')
        booleanParam(name: 'RUN_TESTS', defaultValue: true, description: 'Запускать тесты')
    }

    environment {
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = "hgjuty75/student-app:${BUILD_NUMBER}"     // ← ваш Docker Hub
        CONTAINER_NAME = "student-app-${ENVIRONMENT}"
        RELEASE_TAG = "v${BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Клонирование репозитория...'
                git branch: 'main',
                    url: 'https://github.com/hgjuty75/simple-python-app.git',
                    credentialsId: 'github-creds'
            }
        }

        stage('Tests') {
            when { expression { params.RUN_TESTS } }
            stages {
                stage('Unit Tests') {
                    steps {
                        echo 'Запуск юнит-тестов...'
                        sh '''
                            python3 -m venv venv
                            . venv/bin/activate
                            pip install -r requirements.txt
                            python -m unittest test_app.py -v
                        '''
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Сборка Docker-образа...'
                script {
                    docker.build("${DOCKER_IMAGE}")
                }
            }
        }

        stage('Push to Registry') {
            steps {
                echo 'Публикация образа в Docker Hub...'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh """
                echo "${DOCKER_PASS}" | docker login -u "${DOCKER_USER}" --password-stdin
                docker push ${DOCKER_IMAGE}
                docker logout
            """
		}
	    }
        }

        stage('Deploy to Dev') {
            when { expression { params.ENVIRONMENT == 'dev' } }
            steps {
                echo 'Развертывание в среде DEV...'
                sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 8081:5000 \
                      -e STUDENT_NAME='${params.STUDENT_NAME}' \
                      ${DOCKER_IMAGE}
                """
            }
        }

        stage('Deploy to Staging') {
            when { expression { params.ENVIRONMENT == 'staging' } }
            steps {
                echo 'Развертывание в STAGING...'
                sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 8082:5000 \
                      -e STUDENT_NAME='${params.STUDENT_NAME}' \
                      ${DOCKER_IMAGE}
                """
            }
        }

        stage('Approve Production') {
            when { expression { params.ENVIRONMENT == 'production' } }
            steps {
                script {
                    input message: "Подтвердите развертывание в PRODUCTION версии ${RELEASE_TAG}?",
                          ok: "Да, развернуть"
                }
            }
        }

        stage('Deploy to Production') {
            when { expression { params.ENVIRONMENT == 'production' } }
            steps {
                echo 'Развертывание в PRODUCTION...'
                sh """
                    docker stop ${CONTAINER_NAME} || true
                    docker rm ${CONTAINER_NAME} || true
                    docker run -d --name ${CONTAINER_NAME} -p 8083:5000 \
                      -e STUDENT_NAME='${params.STUDENT_NAME}' \
                      ${DOCKER_IMAGE}
                """
            }
        }

        stage('Create Git Tag') {
            when { expression { params.ENVIRONMENT == 'production' } }
            steps {
                script {
                    echo "Создание тега ${RELEASE_TAG}..."
                    withCredentials([usernamePassword(credentialsId: 'github-creds', usernameVariable: 'GIT_USER', passwordVariable: 'GIT_PASS')]) {
                        sh """
                            git tag ${RELEASE_TAG}
                            git push https://${GIT_USER}:${GIT_PASS}@github.com/hgjuty75/simple-python-app.git ${RELEASE_TAG}
                        """
                    }
                }
            }
        }
    }

    post {
    success {
        echo "Pipeline успешно завершён для среды ${params.ENVIRONMENT}"
        telegramSend message: """
            ✅ Сборка *${env.JOB_NAME}* #${env.BUILD_NUMBER} успешно выполнена.
            Среда: ${params.ENVIRONMENT}
            Docker образ: ${DOCKER_IMAGE}
            Подробнее: ${env.BUILD_URL}
        """
    }
    failure {
        telegramSend message: """
            ❌ Сборка *${env.JOB_NAME}* #${env.BUILD_NUMBER} завершилась с ошибкой!
            Среда: ${params.ENVIRONMENT}
            Проверьте консоль: ${env.BUILD_URL}
        """
    }
}
}
