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
  default = "{{ vault_image }}"
}

variable "storage_path" {
  type = string
  default = "{{ DEPLOYMENT_DATA_PATH }}/vault"
}

variable "base_domain" {
  type = string
  default = "{{ TESLA_DOMAIN }}"
}

job "vault" {
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
  group "vault" {
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
      port "vault" {
        to = 8200
      }
    }

    # Define a task to run
    task "vault" {
      # Use Docker to run the task.
      driver = "docker"

      # Create vault configuration file
      template {
        data = <<EOH
{
  "ui": true,
  "backend": {
    "file": {
      "path": "/vault_data"
    }
  },
  "listener": {
    "tcp": {
      "address": "0.0.0.0:8200",
      "tls_disable": true
    }
  },
  "disable_mlock": true
}
EOH
        destination = "local/local_config.json"
      }

      # Configure Docker driver with the image
      config {
        image   = var.image
        volumes = [
          "${var.storage_path}:/vault_data",
          "local/local_config.json:/local_config.json"
        ]
        ports = ["vault"]
        args = [
          "server",
          "-config",
          "/local_config.json",
        ]
      }

      env {
        SKIP_SETCAP = 1
        VAULT_API_ADDR = "https://vault.${ var.base_domain }"
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "vault"
      tags = [
        "tesla-ce",
        "external",
        "service",
        "vault",
        "traefik.enable=true",
        "traefik.http.routers.vault.rule=Host(`vault.${ var.base_domain }`)",
        "traefik.consulcatalog.connect=true"
      ]
      port = 8200 # "vault"

      check {
        expose   = true
        type     = "http"
        path     = "/v1/sys/health?sealedcode=200&uninitcode=200"
        port     = "vault"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {}
      }
    }
  }
}
