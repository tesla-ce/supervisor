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
  default = "{{ redis_image }}"
}

variable "storage_path" {
  type = string
  default = "{{ DEPLOYMENT_DATA_PATH }}/redis"
}

variable "base_domain" {
  type = string
  default = "{{ TESLA_DOMAIN }}"
}

variable "password" {
  type = string
  default = "{{ REDIS_PASSWORD }}"
}

job "redis" {
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
  group "redis" {
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
      port "redis" {
        to = 6379
      }
    }

    # Define a task to run
    task "redis" {
      # Use Docker to run the task.
      driver = "docker"

      # Configure Docker driver with the image
      config {
        image = var.image
        ports = ["redis"]
        args = [
          "--requirepass \"${ var.password }\""
        ]
        volumes = [
          "${var.storage_path}:/data"
        ]
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "redis"
      port = 6379 # "redis"

      tags = [
        "tesla-ce",
        "external",
        "service",
        "redis",
      ]

      connect {
        sidecar_service {}
      }
    }
  }
}
