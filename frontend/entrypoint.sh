#!/bin/sh

# Create the env-config.js file
echo "window._env_ = {" > /usr/share/nginx/html/env-config.js
for var in $(env | grep VITE_); do
  key=$(echo $var | cut -d '=' -f 1)
  value=$(echo $var | cut -d '=' -f 2-)
  echo "  $key: \"$value\"," >> /usr/share/nginx/html/env-config.js
done
echo "};" >> /usr/share/nginx/html/env-config.js

# Start Nginx
exec "$@"
