pipeline {
    agent any

    triggers {
        cron('H 2 * * *')  // каждый день в 2:00 ночи
    }

    environment {
        PYTHON = 'python'  // или python3, в зависимости от того, как он у тебя установлен
    }

    stages {
        stage('Install dependencies') {
            steps {
                script {
                    bat 'pip install mysql-connector'
                }
            }
        }
        stage('Run Agregation Script') {
            steps {
                echo 'Запуск agregation.py'
                bat "${PYTHON} agregation.py"
            }
        }

        stage('Архивировать CSV') {
            steps {
                echo 'Архивируем результат CSV'
                archiveArtifacts artifacts: 'forum_aggregation.csv', fingerprint: true
            }
        }
    }

    post {
        success {
            echo 'ETL завершён успешно, CSV доступен в Jenkins.'
        }
        failure {
            echo 'Произошла ошибка. Проверь логи.'
        }
    }
}
