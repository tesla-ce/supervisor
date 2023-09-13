# supervisor
TeSLA CE Supervisor

## Get started

You need to execute the following command. If you want to deploy TeSLA in Swarm mode and supervisor in the same server, remember uncomment the line 12 in docker-compose.yml file:

```
docker-compose up -d
```

After that you can open your browser and go to the following URL: http://localhost:5000

Remember there is a folder called data. This folder is used to store the data of the supervisor. If you want to change the location of this folder, you need to change the path in the docker-compose.yml file.

There is complete user guide in tesla-ce.eu website. You can find it in the following link: https://www.tesla-ce.eu/installation/install/supervisor
