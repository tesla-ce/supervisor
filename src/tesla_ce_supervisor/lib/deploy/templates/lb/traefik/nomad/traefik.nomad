variable "count" {
  type = number
  default = 1
}

variable "datacenters" {
  type = list(string)
}

variable "region" {
  type = string
}

variable "image" {
  type    = string
  default = "traefik:v2.5"
}

variable "storage_path" {
  type = string
}

variable "consul_address" {
  type = string
}

variable "consul_scheme" {
  type = string
}

variable "tesla_admin_mail" {
  type = string
}

job "traefik" {
  region      = var.region
  datacenters = var.datacenters
  type        = "service"

  group "traefik" {
    count = var.count

    network {
      mode = "bridge"
      port "http" {
        static = 80
        to = 80
      }

      port "https" {
        static = 443
        to = 443
      }

      # TODO: Remove after testing
      port "api" {
        static = 8081
        to = 8081
      }
    }

    service {
      name = "traefik-http"
      port = "http"
      tags = ["tesla-ce", "http", "traefik"]
      task = "traefik"

      check {
        name     = "alive"
        type     = "tcp"
        port     = "http"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        native = true
      }
    }

    service {
      name = "traefik-https"
      port = "https"
      tags = ["tesla-ce", "https", "traefik"]
      task = "traefik"

      check {
        name     = "alive"
        type     = "tcp"
        port     = "https"
        interval = "10s"
        timeout  = "2s"
      }
    }

    task "traefik" {
      driver = "docker"

      config {
        image        = var.image
        volumes = [
          "${var.storage_path}:/letsencrypt/",
          "local/traefik.toml:/etc/traefik/traefik.toml"
        ]
      }

      template {
        data        = <<EOF
[entryPoints]
    [entryPoints.http]
        address = ":80"
    [entryPoints.https]
        address = ":443"

    #TODO: Remove on production version
    [entryPoints.traefik]
        address = ":8081"

[api]
    dashboard = true
    insecure  = true

[certificatesResolvers.tesla-tlschallenge.acme]
    email = "${ var.tesla_admin_mail }"
    storage = "/letsencrypt/acme.json"
    [certificatesResolvers.tesla-tlschallenge.acme.httpChallenge]
        # used during the challenge
        entryPoint = "http"

# Enable Consul Catalog configuration backend.
[providers.consulCatalog]
    prefix            = "traefik"
    servicename       = "traefik-http"
    exposedByDefault  = false
    connectAware      = true
    #connectByDefault = true
    #[providers.consulCatalog.endpoint]
    #    address = "${var.consul_address}"
    #    scheme  = "${var.consul_scheme}"

EOF
        destination = "local/traefik.toml"
      }

      resources {
        cpu    = 100
        memory = 128
      }
    }
  }
}
