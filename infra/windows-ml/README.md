# Connect Immich on the Pi to the Windows GPU

This setup uses Immich v3.4.1 on the Pi and the matching CUDA image on Windows. It assumes Docker Desktop is running Linux containers with WSL2 GPU support, and that Windows can SSH into the Pi. The worker accepts unauthenticated inference requests. Its Windows port binds to loopback, and the Pi exposes the tunnel only on Immich's Docker bridge. [Immich remote ML guide](https://docs.immich.app/guides/remote-machine-learning/)

### 1. Start the worker on Windows

From the repository root in PowerShell, run the following commands. The first check should show the RTX 5090 inside the container. The second checks the local worker's HTTP endpoint.

```powershell
docker compose -f infra/windows-ml/compose.yml up -d
docker compose -f infra/windows-ml/compose.yml exec immich-machine-learning nvidia-smi -L
curl.exe -fsS http://127.0.0.1:3003/ping
```

### 2. Forward the Pi's loopback port to the Windows worker

Replace `PI_USER@PI_HOST` with your SSH target. Verify its host key on the first connection. Keep the SSH session open while using the worker. After Windows restarts or the connection drops, reestablish the tunnel.

```powershell
ssh -NT -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -R 127.0.0.1:33003:127.0.0.1:3003 PI_USER@PI_HOST
```

On the Pi, `curl -fsS http://127.0.0.1:33003/ping` should now reach the Windows worker. Immich runs in a container with its own loopback interface. The next step makes the tunnel reachable from that container.

### 3. Bind the proxy to the Immich bridge on the Pi

List the networks attached to the Immich server. Select its application network and locate the Linux bridge interface that owns the displayed gateway address.

```sh
sudo docker inspect immich_server --format '{{range $name, $net := .NetworkSettings.Networks}}{{println $name $net.Gateway}}{{end}}'
ip -br -4 addr
```

Use this socket unit at `~/.config/systemd/user/nais-immich-ml.socket`, substituting the actual IPv4 gateway for `BRIDGE_GATEWAY` and the interface name for `BRIDGE_INTERFACE`. Create the directory first if needed.

```ini
[Unit]
Description=Immich inference endpoint on the Pi Docker bridge

[Socket]
ListenStream=BRIDGE_GATEWAY:3003
BindToDevice=BRIDGE_INTERFACE
```

Place the paired service at `~/.config/systemd/user/nais-immich-ml.service` on Raspberry Pi OS.

```ini
[Unit]
Description=Forward inference requests to the Windows SSH tunnel

[Service]
Type=notify
ExecStart=/usr/lib/systemd/systemd-socket-proxyd 127.0.0.1:33003
```

With the bridge up, run `systemctl --user daemon-reload` and `systemctl --user start nais-immich-ml.socket`. Start the socket again after a Pi reboot. If Docker recreates the network, check the gateway and interface again. The deployed Windows tunnel launcher also starts the Pi socket when it reconnects.

### 4. Select the endpoint and verify inference

In Immich **Administration → Settings → Machine Learning**, set the sole endpoint to `http://BRIDGE_GATEWAY:3003`, using the same gateway as above. In this deployment the Pi's local ML Compose service is disabled. Keep Windows and Pi Immich versions aligned when upgrading.

On Windows, follow the worker logs with `docker compose -f infra/windows-ml/compose.yml logs -f immich-machine-learning`. Upload a new test photo to Immich and check **Administration → Jobs**. Verify that Smart Search completes, that the Windows worker logs model execution with the CUDA execution provider during the test, and that the photo can be found with a relevant text query. The first run can take longer while the worker downloads its model. GPU visibility and a successful ping alone only verify the connection and device setup.

With Windows offline, uploads, thumbnails, and timeline browsing continue on the Pi. Once Windows and the tunnel return, use **Missing** for Smart Search and Face Detection to retry missed work. [Immich remote processing and retry behavior](https://docs.immich.app/guides/remote-machine-learning/#forcing-remote-processing)
