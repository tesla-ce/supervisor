variable "count" {
  type = number
  default = {{ count }}
}

variable "datacenters" {
  type = list(string)
  default = {{ nomad_datacenters|safe }}
}

variable "region" {
  type = string
  default = "{{ nomad_region }}"
}

variable "image" {
  type    = string
  default = "{{ tesla_ce_image }}"
}

variable "vault_mount_path_kv" {
  type = string
  default = "{{ VAULT_MOUNT_PATH_KV }}"
}

variable "vault_mount_path_approle" {
  type = string
  default = "{{ VAULT_MOUNT_PATH_APPROLE }}"
}

variable "role_id" {
  type = string
  default = "{{ API_VAULT_ROLE_ID }}"
}

variable "secret_id" {
  type = string
  default = "{{ API_VAULT_SECRET_ID }}"
}

variable "base_domain" {
  type = string
  default = "{{ TESLA_DOMAIN }}"
}

job "tesla_ce_lapi" {
  # Run the job in the global region, which is the default.
  region = var.region

  # Specify the datacenters within the region this job can run in.
  datacenters = var.datacenters

  # Service type jobs optimize for long-lived services. This is
  # the default but we can change to batch for short-lived tasks.
  # type = "service"

  # Priority controls our access to resources and scheduling priority.
  # This can be 1 to 100, inclusively, and defaults to 50.
  # priority = 50

  # Restrict our job to only linux. We can specify multiple
  # constraints as needed.
  #constraint {
  #        attribute = "${node.class}"
  #        value     = "node"
  #}

  # Create a 'minio' group. Each task in the group will be
  # scheduled onto the same machine.
  group "lapi" {
    # Control the number of instances of this group.
    # Defaults to 1
    count = var.count

    # Configure the restart policy for the task group. If not provided, a
    # default is used based on the job type.
    restart {
      # The number of attempts to run the job within the specified interval.
      attempts = 2
      interval = "1m"

      # A delay between a task failing and a restart occurring.
      delay = "10s"

      # Mode controls what happens when a task has restarted "attempts"
      # times within the interval. "delay" mode delays the next restart
      # till the next interval. "fail" mode does not restart the task if
      # "attempts" has been hit within the interval.
      mode = "fail"
    }

    network {
      mode = "bridge"
      port "web" {
        to = 5000
      }
    }

    # Define a task to run
    task "tesla_ce_lapi" {
      # Use Docker to run the task.
      driver = "docker"

      # Configure Docker driver with the image
      config {
        image = var.image
        ports = ["web"]
      }

      env = {
        "SECRETS_PATH"             = "/secrets"
        "VAULT_URL"                = var.vault_url
        "VAULT_ROLE_ID_FILE"       = "/secrets/ROLE_ID"
        "VAULT_SECRET_ID_FILE"     = "/secrets/SECRET_ID"
        "VAULT_MOUNT_PATH_KV"      = var.vault_mount_path_kv
        "VAULT_MOUNT_PATH_APPROLE" = var.vault_mount_path_approle
      }

      # Store secrets
      template {
        data = "${ var.role_id }"
        destination = "secrets/ROLE_ID"
      }
      template {
        data = "${ var.secret_id }"
        destination = "secrets/SECRET_ID"
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "lapi"
      port = 5000

      tags = [
        "tesla-ce",
        "lapi",
        "traefik.enable=true",
        "traefik.http.routers.supervisor.rule=Host(`${var.base_domain}`) && PathPrefix(`/lapi`)",
        "traefik.consulcatalog.connect=true",
      ]

      check {
        expose   = true
        type     = "http"
        path     = "/nginx/status"
        port     = "web"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {
          proxy {
            upstreams {
               destination_name = "mysql-server"
               local_bind_port = 3306
            }
            upstreams {
               destination_name = "minio-api"
               local_bind_port = 9000
            }
            upstreams {
               destination_name = "vault"
               local_bind_port = 8200
            }
            upstreams {
               destination_name = "rabbitmq"
               local_bind_port = 5672
            }
            upstreams {
               destination_name = "rabbitmq-management"
               local_bind_port = 15672
            }
            upstreams {
               destination_name = "redis"
               local_bind_port = 6379
            }
          }
        }
      }
    }
  }
}
