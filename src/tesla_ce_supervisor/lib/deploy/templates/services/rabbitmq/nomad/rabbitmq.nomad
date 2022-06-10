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
  default = "{{ rabbitmq_image }}"
}

variable "storage_path" {
  type = string
  default = "{{ DEPLOYMENT_DATA_PATH }}/rabbitmq"
}

variable "base_domain" {
  type = string
  default = "{{ TESLA_DOMAIN }}"
}

variable "user" {
  type = string
  default = "{{ RABBITMQ_ADMIN_USER }}"
}

variable "password" {
  type = string
  default = "{{ RABBITMQ_ADMIN_PASSWORD }}"
}

variable "erlang_cookie" {
  type = string
  default = "{{ RABBITMQ_ERLANG_COOKIE }}"
}

job "rabbitmq" {
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
  group "rabbitmq" {
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
      port "rabbitmq" {
        to = 5672
      }
      port "rabbitmq_management" {
        to = 15672
      }
    }

    # Define a task to run
    task "rabbitmq" {
      # Use Docker to run the task.
      driver = "docker"

      # Store configuration files
      template {
        data =<<EOH
        [rabbitmq_management,rabbitmq_peer_discovery_consul].
        EOH
        destination = "local/enabled_plugins"
      }
      template {
        data = <<EOH
        cluster_formation.peer_discovery_backend = consul
        cluster_formation.consul.host = {% templatetag openvariable %} env "attr.unique.network.ip-address" {% templatetag closevariable %}
        EOH
        destination = "local/rabbitmq.conf"
      }

      # Store secrets
      template {
        data = "${ var.user }"
        destination = "secrets/USER"
      }
      template {
        data = "${ var.password }"
        destination = "secrets/PASSWORD"
      }

      env = {
        "RABBITMQ_DEFAULT_USER_FILE" = "/secrets/USER"
        "RABBITMQ_DEFAULT_PASS_FILE" = "/secrets/PASSWORD"
        "RABBITMQ_ERLANG_COOKIE" = var.erlang_cookie
      }

      # Configure Docker driver with the image
      config {
        image = var.image
        ports = ["rabbitmq", "rabbitmq_management"]
        volumes = [
          "local/enabled_plugins:/etc/rabbitmq/enabled_plugins",
          "local/rabbitmq.conf:/etc/rabbitmq/rabbitmq.conf",
          "${var.storage_path}:/var/lib/rabbitmq"
        ]
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "rabbitmq"
      port = 5672 # "rabbitmq"

      tags = [
        "tesla-ce",
        "external",
        "service",
        "rabbitmq",
      ]

      connect {
        sidecar_service {}
      }
    }
    service {
      name = "rabbitmq-management"
      port = 15672 # "rabbitmq_management"

      tags = [
        "tesla-ce",
        "external",
        "service",
        "rabbitmq-management",
        "traefik.enable=true",
        "traefik.http.routers.rabbitmq-management.rule=Host(`rabbitmq.${var.base_domain}`)" ,
        "traefik.consulcatalog.connect=true",
      ]

      check {
        expose   = true
        type     = "http"
        path     = "/"
        port     = "rabbitmq_management"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {}
      }
    }
  }
}
