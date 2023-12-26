# HAProxy IPv6 DEMUX
The goal of this project is to demultiplex all incoming connections on HAProxy to a range of randomly selected IPv6 addresses from a specified range that updates over time.

This method can fool basic network inspection devices that block single IPs based on their traffic or protocol.

To use this method, first, you need to configure the remote server to accept requests over a range of IPv6 addresses instead of a single IPv6.

It only works with service providers that route the entire IPv6 block to your server, not just a single IPv6.

This manual has been tested on Ubuntu 22.04.

On your remote server, create a `/etc/netplan/60-ipv6.yaml` file with the following content:
```
network:
  version: 2
  ethernets:
    lo:
      routes:
      - to: 2001:DB8::/64
        scope: host
        type: local
```
Replace `2001:DB8::/64` with the IPv6 range assigned to your server, noting that it is a network address that ends with `::`.

Then run this command to apply the changes:
```
netplan apply
```
Now, you should be able to ping any address from this range:
```
ping6 2001:DB8::1234
```
On the local server, you need to install Docker. You can install Docker with this command:
```
curl -fsSL https://get.docker.com | bash
```
Then, enable ip6tables support for Docker by creating an `/etc/docker/daemon.json` file with the following content:
```
{
  "experimental": true,
  "ip6tables": true
}
```
Restart the Docker daemon:
```
systemctl restart docker
```
Clone this repository on your local server and change the directory to it:
```
git clone https://github.com/aleskxyz/haproxy-ipv6-demux.git
cd haproxy-ipv6-demux
```
Edit the `config.env` file and update `SUBNET` with the IPv6 subnet of the remote server:
```
SUBNET=2001:DB8::/64
IP_COUNT=100
INTERVAL=3600
```
Replace `2001:DB8::/64` with the IPv6 range assigned to your server, noting that it is a network address that ends with `::`.

Now, you can run Docker Compose to start HAProxy and its config generator:
```
docker compose up -d
```
This will bring up HAProxy, listening on ports 80 and 443, and redirect requests to ports 80 and 443 of the remote server.

You can change the HAProxy configuration template by editing `config_generator/haproxy.cfg.j2` and restart the docker compose.

It is recommended to tune kernel parameters on the local server by creating the `/etc/sysctl.d/99-tune-network.conf` file with the following content:
```
fs.file-max = 200000
net.core.rmem_max = 67108864
net.core.wmem_max = 67108864
net.core.netdev_max_backlog = 250000
net.core.somaxconn = 4096
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 10
net.ipv4.tcp_keepalive_time = 600
net.ipv4.ip_local_port_range = 10000 65000
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_max_tw_buckets = 5000
net.ipv4.tcp_fastopen = 3
net.ipv4.tcp_mem = 25600 51200 102400
net.ipv4.tcp_rmem = 4096 65536 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
net.ipv4.tcp_mtu_probing = 1
net.core.default_qdisc=fq
net.ipv4.tcp_congestion_control=bbr
net.netfilter.nf_conntrack_max=1000000
```
Apply the changes with this command:
```
sysctl -p /etc/sysctl.d/99-tune-network.conf
```