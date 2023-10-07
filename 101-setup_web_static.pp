include stdlib

# Update the packages on the computer
exec { 'Update lists':
    command => '/usr/bin/apt update'
}

# Install Nginx on the webserver
package { 'nginx':
    ensure  => 'present',
    require => Exec['Update lists']
}

# Create the necessary directory tree as requested
exec { 'Create Directory Tree':
    command => '/bin/mkdir -p /data/web_static/releases/test /data/web_static/shared',
    require => Package['nginx']
}

$head = "  <head>\n  </head>"
$body = "  <body>\n    Holberton School\n  </body>"
$index = "<html>\n${head}\n${body}\n</html>\n"

# Make the fake HTML file
# to confirm Nginx is working the way it supposed to work
file { 'Create Fake HTML':
    ensure  => 'present',
    path    => '/data/web_static/releases/test/index.html',
    content => $index,
    require => Exec['Create Directory Tree']
}

# Make a symbolic link between /current and /test
file { 'Create Symbolic Link':
    ensure  => 'link',
    path    => '/data/web_static/current',
    force   => true,
    target  => '/data/web_static/releases/test',
    require => File['Create Fake HTML']
}

# Check agian to make sure that Nginx is running
service { 'nginx':
    ensure  => 'running',
    enable  => true,
    require => Package['nginx']
}

# Give permission to users as desired
exec { 'Set permissions':
    command => '/bin/chown -R ubuntu:ubuntu /data',
    require => File['Create Symbolic Link']
}

# Set where the webpage can be found on the webserver 
$loc_header='location /hbnb_static/ {'
$loc_content='alias /data/web_static/current/;'
$new_location="\n\t${loc_header}\n\t\t${loc_content}\n\t}\n"

# Ensure that Nginx also serves the webpage when requested
file_line { 'Set Nginx Location':
    ensure  => 'present',
    path    => '/etc/nginx/sites-available/default',
    after   => 'server_name \_;',
    line    => $new_location,
    notify  => Service['nginx'],
    require => Exec['Set permissions']
}
