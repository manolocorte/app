docker run --rm --network sonarnet -e SONAR_HOST_URL="http://172.18.0.2:9000/" -e SONAR_LOGIN="sqp_91d735926d24cf1c4226f0d13ac65315f4385524" -v C:\Users\Usuario\Desktop\TFG\app\app\main:/usr/src/ sonarsource/sonar-scanner-cli -Dsonar.projectKey=TFG -Dsonar.sonar.projectName="TFG" -Dsonar.sonar.projectVersion=1.0 -Dsonar.sonar.sourceEncoding=UTF-8 > sonarLogs.txt


#   sonar-scanner \
#  -Dsonar.projectKey=TFG \
#  -Dsonar.sources=. \
#  -Dsonar.host.url=http://localhost:9000 \
#  -Dsonar.login=sqp_91d735926d24cf1c4226f0d13ac65315f4385524