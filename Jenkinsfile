pipeline {
   agent {

    label 'ec2-agent'
      //We can use container as agent 
    // docker {
    //     image 'mohamedmabrouk123/to-do-list-tools:latest' // we will create it
    //     args '-v /var/run/docker.sock:/var/run/docker.sock'

    // }
}


    environment {
        GIT_REPO = "https://github.com/mohamedmabrouk-666/To-Do-List"
        BRANCH = "main"
       
       IMAGE_TAG = "${BUILD_NUMBER}"
       IMAGE_REPO_NAME = "mohamedmabrouk123/to_do_list_image"
       FULL_IMAGE_NAME = "${IMAGE_REPO_NAME}:${IMAGE_TAG}"

      AWS_DEFAULT_REGION    = "us-west-1"
    }

   
    stages {
        stage("Clone Github Repo") {
            steps {
                git branch: 'main', credentialsId: 'githubtoken',
                    url: "${GIT_REPO}"
            }
        }

        stage("Build Docker image") {
            steps {
                script {
                    sh "docker build -t ${FULL_IMAGE_NAME} ."
                }
            }
        }
       
        stage("Login to DockerHub") {
            steps {
                withCredentials([usernamePassword(
                   //DockerhubLogin is a (token from Dockerhub && User Name) ==> To save our infromation
                    credentialsId: 'DockerhubLogin',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    // to connect Jenkines with dockerhub
                    sh 'echo $PASS | docker login -u $USER --password-stdin'
                    // to push our image into dockerhub
                    sh "docker push ${FULL_IMAGE_NAME}"
                
                }
            }
        }
//------
       stage("Update Kubernetes Manifest (GitOps)") {
   steps {
       //githubtoken is a (token from GitHub) ==> To save our infromation
      withCredentials([usernamePassword(
         credentialsId: 'githubtoken',
         usernameVariable: 'GIT_USER',
         passwordVariable: 'GIT_PASS'
      )]) {

          // User EC2 on AWS ad Cluster and use ArgoCD to automate between cluster and GitHub
         sh '''
         cd K8s
           
        sed -i "s|image:.*|image: ${FULL_IMAGE_NAME}|" deployment.yaml

         git config user.email "jenkins@ci.com"
         git config user.name "jenkins"

        git add deployment.yaml
         git commit -m "update image version from Jenkins"

         git push https://${GIT_USER}:${GIT_PASS}@github.com/mohamedmabrouk-666/To-Do-List.git main
         '''
      }
   }
}
    }


post {
    always {

        echo "Cleaning Docker resources..."

        sh '''
        docker system prune -af
        '''
    }

    success {
        echo "Pipeline completed successfully"
    }

    failure {
        echo "Pipeline failed"
    }
}

}
