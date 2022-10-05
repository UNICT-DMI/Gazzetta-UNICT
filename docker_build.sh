docker stop bot
docker rm bot
docker build --tag gazzetta-unict .
docker run -it \
--name bot \
--mount type=bind,source="$(pwd)/data",destination=/app/data \
gazzetta-unict