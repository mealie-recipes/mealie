# Using SWAG as Reverse Proxy

!!! info
	This guide was submitted by a community member. Find something wrong? Submit a PR to get it fixed!


To make the setup of a Reverse Proxy much easier, Linuxserver.io developed [SWAG](https://github.com/linuxserver/docker-swag)  
SWAG - Secure Web Application Gateway (formerly known as letsencrypt, no relation to Let's Encrypt™) sets up an Nginx web server and reverse proxy with PHP support and a built-in certbot client that automates free TLS server certificate generation and renewal processes (Let's Encrypt and ZeroSSL). It also contains fail2ban for intrusion prevention.

## Step 1: Get a domain

The first step is to grab a dynamic DNS if you don't have your own subdomain already. You can get this from for example [DuckDNS](https://www.duckdns.org).
If you already own a domain, you'll need to create an `A` record that points to the machine that SWAG is running on. See 
the [SWAG documentation](https://docs.linuxserver.io/general/swag#create-container-via-http-validation) for more details.

## Step 2: Set-up SWAG

Then you will need to set up SWAG, the variables of the docker-compose are explained on the Github page of [SWAG](https://github.com/linuxserver/docker-swag).
This is an example of how to set it up using DuckDNS and docker-compose.

!!! example "docker-compose.yml"
```yaml
version: "2.1"
services:
    swag:
        image: ghcr.io/linuxserver/swag
        container_name: swag
        cap_add:
            - NET_ADMIN
        environment:
            - PUID=1000
            - PGID=1000
            # valid TZs at https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
            - TZ=Europe/Brussels 
            - URL=<mydomain.duckdns>
            - SUBDOMAINS=wildcard
            - VALIDATION=duckdns
            - CERTPROVIDER= #optional
            - DNSPLUGIN= #optional
            - DUCKDNSTOKEN=<duckdnstoken>
            - EMAIL=<e-mail> #optional
            - ONLY_SUBDOMAINS=false #optional
            - EXTRA_DOMAINS=<extradomains> #optional
            - STAGING=false #optional
        volumes:
            - /etc/config/swag:/config
        ports:
            - 443:443
            # required if VALIDATION=http above, if you aren't using DuckDNS
            - 80:80 
        restart: unless-stopped

```

Don't forget to change the `mydomain.duckns` into your personal domain and the `duckdnstoken` into your token and remove the brackets.

You can also include the contents of the [mealie docker-compose](mealie/documentation/getting-started/install/#docker-compose-with-sqlite) in the SWAG
docker-compose, without the `ports` section under mealie. This allows SWAG and mealie to communicate on the same docker network, without
making mealie visible to other applications on your machine.

## Step 3: Change the config files

Navigate to the config folder of SWAG and head to `proxy-confs`. If you used the example above, you should navigate to: `/etc/config/swag/nginx/proxy-confs/`.
There are a lot of preconfigured files to use for different apps such as radarr, sonarr, overseerr, ...

To use the bundled configuration file, simply rename `mealie.subdomain.conf.sample` in the proxy-confs folder to `mealie.subdomain.conf`.
Alternatively, you can create a new file `mealie.subdomain.conf` in proxy-confs with the following configuration:

!!! example "mealie.subdomain.conf"
```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name mealie.*;

    include /config/nginx/ssl.conf;

    client_max_body_size 0;

    location / {
        include /config/nginx/proxy.conf;
        include /config/nginx/resolver.conf;
        set $upstream_app mealie;
        set $upstream_port 80;
        set $upstream_proto http;
        proxy_pass $upstream_proto://$upstream_app:$upstream_port;
    }
}	
```

## Step 4: Port-forward port 443

Since SWAG allows you to set up a secure connection, you will need to open port 443 on your router for encrypted traffic. This is way more secure than port 80 for http. For more information about using TLS on port 443, see [SWAG's documentation](https://docs.linuxserver.io/general/swag#cert-provider-lets-encrypt-vs-zerossl) on cert providers and port forwarding.

## Step 5: Restart SWAG

When you change anything in the config of Nginx, you will need to restart the container using `docker restart swag`.
If everything went well, you can now access mealie on the subdomain you configured: `mealie.mydomain.duckdns.org`
