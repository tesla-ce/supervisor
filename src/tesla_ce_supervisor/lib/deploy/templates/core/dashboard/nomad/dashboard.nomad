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
  default = "{{ dashboard_image }}"
}

variable "base_domain" {
  type = string
  default = "{{ TESLA_DOMAIN }}"
}

job "tesla_ce_dashboard" {
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

  # Create a 'dashboard' group. Each task in the group will be
  # scheduled onto the same machine.
  group "tesla_ce_dashboard" {
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
      port "http" {
        to = 80
      }
    }

    # Define a task to run
    task "tesla_ce_dashboard" {
      # Use Docker to run the task.
      driver = "docker"

      # Configure Docker driver with the image
      config {
        image   = var.image
        ports = ["http"]
      }

      env {
        API_URL = "https://${ var.base_domain }/api/v2"
      }

      resources {
        cpu    = 300
        memory = 300
      }
    }
    service {
      name = "dashboard"
      tags = [
        "tesla-ce",
        "dashboard",
        "traefik.enable=true",
        "traefik.http.routers.dashboard.rule=Host(`${ var.base_domain }`) && PathPrefix(`/ui/`)",
        "traefik.consulcatalog.connect=true"
      ]
      port = 80 # "http"

      check {
        expose   = true
        type     = "http"
        path     = "/"
        port     = "http"
        interval = "10s"
        timeout  = "2s"
      }

      connect {
        sidecar_service {}
      }
    }
  }
}
