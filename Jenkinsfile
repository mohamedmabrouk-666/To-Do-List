pipeline {
   agent {

    label 'ec2-agent'
    // docker {
    //     image 'mohamedmabrouk123/to-do-list-tools:latest' // we will create it
    //     args '-v /var/run/docker.sock:/var/run/docker.sock'

    // }
}


    environment {
        GIT_REPO = "https://github.com/mohamedmabrouk-666/To-Do-List"
        BRANCH = "main"
       
       IMAGE_REPO_NAME = "to_do_list_image"
       IMAGE_TAG = "${BUILD_NUMBER}"
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
    //    stage("Tag our image"){
    //         steps{
    //    sh "docker tag to_do_list_image mohamedmabrouk123/to_do_list:latest"
    //         }
    //    }
        stage("Login to DockerHub") {
            steps {
                withCredentials([usernamePassword(
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
      withCredentials([usernamePassword(
         credentialsId: 'githubtoken',
         usernameVariable: 'GIT_USER',
         passwordVariable: 'GIT_PASS'
      )]) {

         sh '''
         cd K8s

        sed -i "s|image:.*|image: ${FULL_IMAGE_NAME}|" K8s/deployment.yaml

         git config user.email "jenkins@ci.com"
         git config user.name "jenkins"

        git add K8s/deployment.yaml
         git commit -m "update image version from Jenkins"

         git push https://${GIT_USER}:${GIT_PASS}@github.com/mohamedmabrouk-666/To-Do-List.git main
         '''
      }
   }
}
// --------------------------------------------------
//         stage("Terraform Apply") {
//            steps {
//                   // withCredentials([usernamePassword(
//                   //   credentialsId: 'EC2_Login',
//                   //   usernameVariable: 'AWS_ACCESS_KEY_ID',
//                   //   passwordVariable: 'AWS_SECRET_ACCESS_KEY'   
//                   //  )])
//                withCredentials([[
//                     $class: 'AmazonWebServicesCredentialsBinding',
//                     credentialsId: 'AWS_Login'
//                 ]])
//               {

//                  sh '''
//             export AWS_DEFAULT_REGION=us-west-1
//             echo "Terraform commands"
//             cd terraform
//             terraform init
//             terraform apply -auto-approve
//             '''
                 
//         }
//     }
// }
       
 
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
