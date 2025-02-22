@echo off
docker image prune -f 
docker volume prune -f
docker-compose %*
exit /b