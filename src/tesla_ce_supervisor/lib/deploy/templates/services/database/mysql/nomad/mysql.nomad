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
  default = "{{ db_image }}"
}

variable "storage_path" {
  type = string
  default = "{{ DEPLOYMENT_DATA_PATH }}/db"
}

variable "db_root_password" {
  type = string
  default = "{{ DB_ROOT_PASSWORD }}"
}

variable "db_password" {
  type = string
  default = "{{ DB_PASSWORD }}"
}

variable "db_user" {
  type = string
  default = "{{ DB_USER }}"
}

variable "db_name" {
  type = string
  default = "{{ DB_NAME }}"
}

job "mysql" {
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
  group "mysql" {
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
      port "mysql" {
        to = 3306
      }
    }

    # Define a task to run
    task "mysql" {
      # Use Docker to run the task.
      driver = "docker"

      # Configure Docker driver with the image
      env = {
        "MYSQL_ROOT_PASSWORD_FILE" = "/secrets/DB_ROOT_PASSWORD"
        "MYSQL_DATABASE" = var.db_name
        "MYSQL_USER" = var.db_user
        "MYSQL_PASSWORD_FILE" = "/secrets/DB_PASSWORD"
      }

      config {
        image = var.image
        ports = ["mysql"]
        volumes = [
          "${var.storage_path}:/var/lib/mysql"
        ]
      }

      # Store secrets
      template {
        data = "${ var.db_root_password }"
        destination = "secrets/DB_ROOT_PASSWORD"
      }
      template {
        data = "${ var.db_password }"
        destination = "secrets/DB_PASSWORD"
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "mysql-server"
      port = 3306 # "mysql"

      tags = [
        "tesla-ce",
        "external",
        "service",
        "mysql",
      ]

      connect {
        sidecar_service {}
      }
    }
  }
}
