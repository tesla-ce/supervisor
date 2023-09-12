Configure docker to listen all addresses in TCP socket.

Add file to /etc/docker/daemon.json with this content:
```
{
	"hosts": ["tcp://0.0.0.0:2376", "unix:///var/run/docker.sock"]
}
```

If you want to configure connection with TLS:
```
{
    "tls": true,
    "tlscert": "/var/docker/cert.pem",
    "tlskey": "/var/docker/key.pem",
    "tlscacert": "/var/docker/ca.pem",
	"hosts": ["tcp://0.0.0.0:2376", "unix:///var/run/docker.sock"]
}
```

Create folder:
```
mkdir -p /etc/systemd/system/docker.service.d/
```

Create file:
```
nano /etc/systemd/system/docker.service.d/docker.conf
```

With content:
```
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd
```

Reload daemon:
```
systemctl daemon-reload
```