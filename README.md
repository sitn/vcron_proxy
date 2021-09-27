# Deploy

```powershell
cp .env.sample .env
```

Set your config, then:

```powershell
$env:DOCKER_HOST="root@server.com"
docker-compose up -d
```
