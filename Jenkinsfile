pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                git 'https://github.com/RAbivarsan/devops.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                pip install -r requirements.txt
                '''
            }
        }

        stage('Train Model') {
            steps {
                bat 'python train.py'
            }
        }

        stage('Stop Old App') {
            steps {
                bat '''
                taskkill /F /IM python.exe || echo No process
                '''
            }
        }

        stage('Run App') {
            steps {
                bat '''
                start /B python app.py
                '''
            }
        }
    }
}