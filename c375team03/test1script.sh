pipeline {
    agent {
        node {
            label 'generic-agent'
        }
    }
    stages {
        stage('Check home screen') {
            steps {
                script {
                    sh """
                    curl https://c375team03dev.computerlab.online/
                    """
                }
            }
        }
        
        stage('Check login page'){
            
            steps{
                script{
                    sh """
                    curl "https://c375team0dev.computerlab.online/login"
                    """
                }
            }
        }
        
        stage('Check quotes page') {
            steps {
                script {
                    sh """
                    curl "https://c375team03dev.computerlab.online/quotes"
                    """
                }
            }
        }
                stage('Check portfolio page'){
            
            steps{
                script{
                    sh """
                    curl "https://c375team03dev.computerlab.online/portfolio"
                    """
                }
            }
        }
                stage('Check orderbook page') {
            steps {
                script {
                    sh """
                    curl "https://c375team03dev.computerlab.online/orderbook"
                    """
                }
            }
        }
                        stage('Check /trade api'){
            
            steps{
                script{
                    sh """
                    curl -X 'POST' \
  'https://c375team03dev-api.computerlab.online/trade' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "sessionid": "",
  "uname": "",
  "shares": 0,
  "symbol": ""
}'
                    """
                }
            }
        }
    }
}
