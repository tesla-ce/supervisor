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

variable "base_domain" {
  type = string
  default = "{{ TESLA_DOMAIN }}"
}

variable "image" {
  type    = string
  default = "{{ command_image }}"
}

variable "command" {
  type    = string
  default = "{{ command }}"
}

variable "command_arguments" {
  type = list(string)
  default = {{ command_arguments|safe }}
}

variable "supervisor_remote_url" {
  type = string
  default = "{{ SUPERVISOR_REMOTE_URL|safe }}"
}

job "supervisor_command" {
  # Run the job in the global region, which is the default.
  region = var.region

  # Specify the datacenters within the region this job can run in.
  datacenters = var.datacenters

  # Set type as batch to run and end
  type = "batch"

  # Priority controls our access to resources and scheduling priority.
  # This can be 1 to 100, inclusively, and defaults to 50.
  # priority = 50

  # Restrict our job to only linux. We can specify multiple
  # constraints as needed.
  #constraint {
  #        attribute = "${node.class}"
  #        value     = "node"
  #}

  # Create a 'supervisor_command' group. Each task in the group will be
  # scheduled onto the same machine.
  group "supervisor_command" {
    # Control the number of instances of this group.
    # Defaults to 1
    count = var.count

    network {
      mode = "bridge"
    }

    # Define a task to run
    task "supervisor_command" {
      # Use Docker to run the task.
      driver = "docker"

      # Configure Docker driver with the image
      config {
        image = var.image
        command = var.command
        args = var.command_arguments
        healthchecks {
          disable = true
        }
      }

      env = {
        "SUPERVISOR_DATA"        = "/data"
        "SECRETS_PATH"           = "/secrets"
        "TESLA_DOMAIN"           = var.base_domain
        "DJANGO_SETTINGS_MODULE" = "tesla_ce.settings"
        "DJANGO_CONFIGURATION"   = "Setup"
        "SETUP_MODE"             = "SETUP"
        "SUPERVISOR_REMOTE_URL"  = var.supervisor_remote_url
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "supervisor-command"
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
