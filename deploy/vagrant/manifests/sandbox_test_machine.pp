import "sandbox-base.pp"

class sandbox_rpm_dev inherits sandbox_rpm {
    File['sandbox.repo'] {
        path    => "/etc/yum.repos.d/sandbox.repo",
        content => template("/vagrant/files/sandbox.repo"),
    }
}

include sandbox_rpm_dev
