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
  default = "{{ minio_image }}"
}

variable "storage_path" {
  type = string
  default = "{{ DEPLOYMENT_DATA_PATH }}/minio"
}

variable "base_domain" {
  type = string
  default = "{{ TESLA_DOMAIN }}"
}

variable "storage_region" {
  type = string
  default = "{{ STORAGE_REGION }}"
}

variable "access_key" {
  type = string
  default = "{{ STORAGE_ACCESS_KEY }}"
}

variable "secret_key" {
  type = string
  default = "{{ STORAGE_SECRET_KEY }}"
}

job "minio" {
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
  group "minio" {
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
      port "minio" {
        to = 9000
      }
      port "minio_console" {
        to = 9001
      }
    }

    # Define a task to run
    task "minio" {
      # Use Docker to run the task.
      driver = "docker"

      # Configure Docker driver with the image
      config {
        image   = var.image
        volumes = [
          "${var.storage_path}:/export",
          "secrets:/var/run/secrets"
        ]
        ports = ["minio", "minio-console"]
        args = [
          "server",
          "/export",
          "--console-address",
          ":9001",
        ]
      }

      # Store secrets
      template {
        data = "${ var.access_key }"
        destination = "secrets/access_key"
      }
      template {
        data = "${ var.secret_key }"
        destination = "secrets/secret_key"
      }

      env {
        MINIO_REGION_NAME = var.storage_region
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "minio-api"
      tags = [
        "tesla-ce",
        "external",
        "service",
        "s3",
        "minio",
        "api",
      ]
      port = 9000 # "minio"

      check {
        expose   = true
        type     = "http"
        path     = "/minio/health/live"
        port     = "minio"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {}
      }
    }
    service {
      name = "minio-console"
      tags = [
        "tesla-ce",
        "external",
        "service",
        "s3",
        "minio",
        "console",
        "traefik.enable=true",
        "traefik.http.routers.minio.rule=Host(`storage.${var.base_domain}`)",
        "traefik.consulcatalog.connect=true"
      ]
      port = 9001 # "minio_console"

      check {
        expose   = true
        type     = "http"
        path     = "/minio/health/live"
        port     = "minio_console"
        interval = "10s"
        timeout  = "2s"
      }
      connect {
        sidecar_service {}
      }
    }
  }
}
