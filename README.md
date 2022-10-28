# vcron_proxy

An internal VCRON proxy.

# Dev

After cloning this repository:

```powershell
python -m venv .venv
./.venv/Scripts/activate
pip install -r requirements.txt
```

Then run flask dev server:

```powershell
flask run
```

## Deploy

```powershell
cp .env.sample .env
```

Set your config, then:

```powershell
$env:DOCKER_HOST="root@server.com"
docker-compose up -d
```
